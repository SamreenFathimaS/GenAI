# app.py
# Requirements:
#   pip install "autogen-agentchat>=0.4.0" "autogen-ext>=0.4.0" flask python-dotenv
#   export/set OPENAI_API_KEY first

import os
import json
import uuid
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from dotenv import load_dotenv
from flask import Flask, request, jsonify

# AutoGen v0.4
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import TextMentionTermination

# =========================
# ENV / APP INIT
# =========================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

app = Flask(__name__)

if not OPENAI_API_KEY:
    raise RuntimeError("Set your OPENAI_API_KEY in your environment or a .env file.")

COMPETENCY_PLAN = [
    "background & role fit",
    "tools & ecosystem used(Excel, SQL, Python/R, BI)",
    "SQL querying & data wrangling",
    "statistics & experimentation",
    "visualization/storytelling (PowerBI/Tableau)",
    "business impact & communication with stakeholders",
    "problem solving under constraints",
    "data governance & quality checks",
]

# =========================
# SESSION STORAGE (IN-MEMORY)
# For production, move to Redis/DB.
# =========================
@dataclass
class InterviewSession:
    session_id: str
    position: str = ""
    history: List[Dict[str, str]] = field(default_factory=list)  # [{role, content}]
    scores: List[Dict[str, Any]] = field(default_factory=list)
    avg_score: float = 0.0
    rounds_done: int = 0
    asked_questions: List[str] = field(default_factory=list)
    next_comp_idx: int = 0
    model_client: Optional[OpenAIChatCompletionClient] = None
    agents: Dict[str, AssistantAgent] = field(default_factory=dict)
    team: Optional[RoundRobinGroupChat] = None
    ended: bool = False

SESSIONS: Dict[str, InterviewSession] = {}


# =========================
# HELPERS
# =========================
def _add_history(ses: InterviewSession, role: str, content: str):
    ses.history.append({"role": role, "content": content})


def _parse_and_store_score(ses: InterviewSession, text: str):
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "score" in data:
            ses.scores.append(data)
            scores = [float(d.get("score", 0)) for d in ses.scores]
            ses.avg_score = sum(scores) / max(1, len(scores))
    except Exception:
        pass


def _last_agent_messages(messages: List[TextMessage], agents: List[str]) -> Dict[str, str]:
    got: Dict[str, str] = {}
    for msg in reversed(messages):
        src = getattr(msg, "source", None)
        if src and src in agents and src not in got:
            got[src] = msg.content
        if len(got) == len(agents):
            break
    return got


async def _run_turn_async(team: RoundRobinGroupChat, task: Optional[str] = None, timeout_sec: int = 60) -> List[TextMessage]:
    try:
        result = await asyncio.wait_for(team.run(task=task), timeout=timeout_sec)
        return result.messages
    except asyncio.TimeoutError:
        return []
    except Exception:
        return []


def _run_turn(team: RoundRobinGroupChat, task: Optional[str] = None, timeout_sec: int = 60) -> List[TextMessage]:
    # Each Flask request runs in its own thread; create a fresh loop per call.
    return asyncio.run(_run_turn_async(team, task, timeout_sec))


def _get_next_competency(ses: InterviewSession) -> str:
    idx = ses.next_comp_idx % len(COMPETENCY_PLAN)
    ses.next_comp_idx += 1
    return COMPETENCY_PLAN[idx]


def _build_team(ses: InterviewSession, position: str):
    model_name = "gpt-4.1"
    client = OpenAIChatCompletionClient(
        model=model_name,
        api_key=OPENAI_API_KEY,
        temperature=0.7,
    )

    interviewer_sys = (
        f"You are a professional interviewer for the role: {position}.\n"
        "- Ask ONE question at a time (multi_part list).\n"
        "- Do not repeat earlier questions verbatim, vary phrasing and topic.\n"
        "- Follow this competency plan over the interview one per question: "
        + "; ".join(COMPETENCY_PLAN) + "\n"
        "- Prefer short, pointed questions tailored to the candidate’s last answer.\n"
        "- Only say 'END' after at least 6 Q&A rounds and when explicitly wrapping up."
    )

    coach_sys = (
        "You are a concise career coach. After the candidate answers, provide 2-3 bullet tips to improve that specific answer.\n"
        "Keep under 80 words. Do NOT ask new questions or evaluate overall performance — be specific."
    )

    scorer_sys = (
        "You are a strict scoring agent. Read ONLY interviewer’s latest question and candidate’s latest answer. "
        'Return strict JSON with keys exactly: { "criteria": ["clarity","relevance","technical_depth"], "score": float, "reasoning": "..." } '
        "Score from 0–10 (half point allowed). No extra text or markdown."
    )

    interviewer = AssistantAgent("interviewer", model_client=client, system_message=interviewer_sys)
    coach = AssistantAgent("coach", model_client=client, system_message=coach_sys)
    scorer = AssistantAgent("scorer", model_client=client, system_message=scorer_sys)
    termination = TextMentionTermination("END")

    team = RoundRobinGroupChat(
        [interviewer, coach, scorer],
        termination_condition=termination,
        max_turns=1,
    )

    ses.model_client = client
    ses.agents = {"interviewer": interviewer, "coach": coach, "scorer": scorer}
    ses.team = team


def _serialize_session(ses: InterviewSession) -> Dict[str, Any]:
    return {
        "session_id": ses.session_id,
        "position": ses.position,
        "history": ses.history,
        "scores": ses.scores,
        "avg_score": ses.avg_score,
        "rounds_done": ses.rounds_done,
        "asked_questions": ses.asked_questions,
        "next_comp_idx": ses.next_comp_idx,
        "ended": ses.ended,
    }


# =========================
# ROUTES
# =========================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/start", methods=["POST"])
def start_interview():
    """
    body: { "position": "Data Analyst" }
    returns: {
      session_id, history, next_question, state...
    }
    """
    data = request.get_json(silent=True) or {}
    position = (data.get("position") or "").strip()
    if not position:
        return jsonify({"error": "position is required"}), 400

    session_id = str(uuid.uuid4())
    ses = InterviewSession(session_id=session_id, position=position)
    SESSIONS[session_id] = ses

    _build_team(ses, position)
    _add_history(ses, "system", f"Interview started for **{position}**.")

    # First question
    comp = _get_next_competency(ses)
    task = (
        "Begin the interview briefly, then ask the FIRST QUESTION.\n"
        f"- Target Competency this turn: **{comp}**\n"
        "- Do not repeat previous question\n"
    )
    msgs = _run_turn(ses.team, task=task)
    q = _last_agent_messages(msgs, ["interviewer"]).get("interviewer", "").strip()
    if not q:
        q = "Welcome! To start, could you briefly introduce yourself?"
    ses.asked_questions.append(q)
    _add_history(ses, "interviewer", q)

    return jsonify({"session": _serialize_session(ses), "next_question": q})


@app.route("/answer", methods=["POST"])
def submit_answer():
    """
    body: { "session_id": "...", "answer": "..." }
    returns:
      {
        coach_tips, score_json, avg_score, next_question, ended, state...
      }
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    answer = (data.get("answer") or "").strip()

    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "valid session_id is required"}), 400
    if not answer:
        return jsonify({"error": "answer is required"}), 400

    ses = SESSIONS[session_id]
    if ses.ended:
        return jsonify({"error": "Interview already ended"}), 400

    _add_history(ses, "user", answer)
    ses.rounds_done += 1

    # Coach responds
    coach_tips = None
    msgs = _run_turn(ses.team, task=answer)
    coach_tips = _last_agent_messages(msgs, ["coach"]).get("coach")
    if coach_tips:
        _add_history(ses, "coach", coach_tips)

    # Scorer responds
    score_json = None
    msgs = _run_turn(ses.team, task="Score the last answer now.")
    score_text = _last_agent_messages(msgs, ["scorer"]).get("scorer")
    if score_text:
        score_json = score_text
        _parse_and_store_score(ses, score_text)
        _add_history(ses, "scorer", f"```json\n{score_text}\n```")

    # Interviewer asks next question
    comp = _get_next_competency(ses)
    previously_asked = "\n".join(ses.asked_questions[-5:]) if ses.asked_questions else "None yet"

    interviewer_task = (
        "Continue interview with the next question.\n"
        f"Target competency this turn: **{comp}**.\n"
        "- Do NOT repeat earlier questions; avoid similar phrasing.\n"
        f"- Previous questions:\n {previously_asked}\n"
        "Prefer short, pointed questions tailored to the candidate’s last answer.\n"
    )

    msgs = _run_turn(ses.team, task=interviewer_task)
    next_q = _last_agent_messages(msgs, ["interviewer"]).get("interviewer", "").strip()

    if next_q == "END" and ses.rounds_done < 6:
        # Force a follow-up instead of ending too early
        msgs = _run_turn(
            ses.team,
            task=(
                "Do not end. Ask a follow-up interview question tailored to the previous answer. "
                "Avoid repeating earlier question; pick a new angle."
            ),
        )
        next_q = _last_agent_messages(msgs, ["interviewer"]).get("interviewer", "").strip()

    if next_q == "END" and ses.rounds_done >= 6:
        ses.ended = True
        _add_history(ses, "interviewer", "Thanks! The interview has concluded.")
        return jsonify({
            "session": _serialize_session(ses),
            "coach_tips": coach_tips,
            "score_json": score_json,
            "avg_score": ses.avg_score,
            "next_question": None,
            "ended": True
        })

    if not next_q:
        next_q = f"Let's talk about {comp}, could you please share a concrete example from your experience?"
    ses.asked_questions.append(next_q)
    _add_history(ses, "interviewer", next_q)

    return jsonify({
        "session": _serialize_session(ses),
        "coach_tips": coach_tips,
        "score_json": score_json,
        "avg_score": ses.avg_score,
        "next_question": next_q,
        "ended": False
    })


@app.route("/state", methods=["GET"])
def get_state():
    """
    query: ?session_id=...
    """
    session_id = request.args.get("session_id", "")
    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "valid session_id is required"}), 400
    ses = SESSIONS[session_id]
    return jsonify({"session": _serialize_session(ses)})


@app.route("/reset", methods=["POST"])
def reset_session():
    """
    body: { "session_id": "..." }
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "valid session_id is required"}), 400
    # Remove the session
    del SESSIONS[session_id]
    return jsonify({"ok": True})


if __name__ == "__main__":
    # For local dev only. Use a production WSGI server in deployment.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=False)
