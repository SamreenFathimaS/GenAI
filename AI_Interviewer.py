# interview_app.py
# Requirements:
#   pip install "autogen-agentchat>=0.4.0" "autogen-ext>=0.4.0" streamlit python-dotenv nest_asyncio
#   export/set OPENAI_API_KEY first

import os
import json
import asyncio
from typing import List, Dict, Optional

import streamlit as st
from dotenv import load_dotenv

# AutoGen v0.4
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import TextMentionTermination

# Allow nested loops inside Streamlit
import nest_asyncio
nest_asyncio.apply()

# =====================================
# ENVIRONMENT SETUP
# =====================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

st.set_page_config(page_title="AI Interviewer(Autogen V0.4)", page_icon="🎤", layout="wide")
st.title("🎤 Realtime AI Interviewer (Autogen V0.4 + Streamlit)")
st.caption("Flow: Interviewer ➝ Candidate ➝ Career Coach ➝ Scorer ➝ Next Question")

if not OPENAI_API_KEY:
    st.warning("Set your OPENAI_API_KEY in your environment or a .env file.", icon="⚠️") 

# =====================================
# SESSION STATE
# =====================================
COMPETENCY_PLAN = [
    "background & role fit",
    "tools & ecosystem used(Excel, SQL, Python/R, BI)",
    "SQL querying & data wrangling",
    "statistics & experimentation",
    "visualization/storytelling (PowerBI/Tableau)",
    "business impact & communication with stakeholders",
    "problem solving under constraints",
    "data governance & quality checks"
]

def _init_state():
    if "started" not in st.session_state:
        st.session_state.started = False
    if "position" not in st.session_state:
        st.session_state.position = " "
    if "history" not in st.session_state:
        st.session_state.history = []  
    if "scores" not in st.session_state:
        st.session_state.scores = []   
    if "avg_score" not in st.session_state:
        st.session_state.avg_score = 0.0
    if "rounds_done" not in st.session_state:
        st.session_state.rounds_done = 0
    if "asked_questions" not in st.session_state:
        st.session_state.asked_questions = []  
    if "next_comp_idx" not in st.session_state:
        st.session_state.next_comp_idx = 0
    if "model_client" not in st.session_state:
        st.session_state.model_client = None
    if "agents" not in st.session_state:
        st.session_state.agents = {}
    if "team" not in st.session_state:
        st.session_state.team = None

_init_state()

# =====================================
# HELPERS
# =====================================
def add_history(role: str, content: str):
    st.session_state.history.append({"role": role, "content": content})

def render_history():
    for h in st.session_state.history:
        with st.chat_message(h["role"]):
            st.markdown(h["content"])

def parse_and_store_score(text: str):
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "score" in data:
            st.session_state.scores.append(data)
            scores = [d.get("score", 0) for d in st.session_state.scores]
            st.session_state.avg_score = sum(scores) / max(1, len(scores))
    except Exception:
        pass

def last_agent_messages(messages: List[TextMessage], agents: List[str]) -> Dict[str, str]:
    got: Dict[str, str] = {}
    for msg in reversed(messages):
        src = getattr(msg, "source", None)
        if src and src in agents and src not in got:
            got[src] = msg.content
        if len(got) == len(agents):
            break
    return got

# =====================================
# RUN TURN (ASYNC SAFE)
# =====================================
async def _run_turn_async(team: RoundRobinGroupChat, task: Optional[str] = None, timeout_sec: int = 60) -> List[TextMessage]:
    try:
        result = await asyncio.wait_for(team.run(task=task), timeout=timeout_sec)
        return result.messages
    except asyncio.TimeoutError:
        add_history("system", "⚠️ Timeout waiting for agent response.")
        return []
    except Exception as e:
        add_history("system", f"⚠️ Runtime error: {e}")
        return []

def run_turn(team: RoundRobinGroupChat, task: Optional[str] = None, timeout_sec: int = 60) -> List[TextMessage]:
    return asyncio.run(_run_turn_async(team, task, timeout_sec))

def reset_all():
    st.session_state.started = False
    st.session_state.position = ""
    st.session_state.history.clear()
    st.session_state.scores.clear()
    st.session_state.avg_score = 0.0
    st.session_state.rounds_done = 0
    st.session_state.asked_questions = []
    st.session_state.next_comp_idx = 0
    st.session_state.team = None
    st.session_state.agents = {}

def get_next_competency() -> str:
    idx = st.session_state.next_comp_idx % len(COMPETENCY_PLAN)
    st.session_state.next_comp_idx += 1
    return COMPETENCY_PLAN[idx]

# =====================================
# SYSTEM PROMPTS (UNCHANGED)
# =====================================
def build_team(position: str):
    model_name = 'gpt-4.1'
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
        "Return strict JSON with keys exactly: "
        '{ "criteria": ["clarity","relevance","technical_depth"], "score": float, "reasoning": "..." } ' 
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

    st.session_state.model_client = client
    st.session_state.agents = {"interviewer": interviewer, "coach": coach, "scorer": scorer}
    st.session_state.team = team

# =====================================
# STREAMLIT UI (UNCHANGED)
# =====================================
with st.sidebar:
    st.subheader("Setup")
    position_input = st.text_input("🎯 Job Position", value=st.session_state.position, placeholder="e.g. Data Analyst")
    col1, col2 = st.columns(2)
    with col1:
        start_disabled = st.session_state.started or not position_input.strip()
        if st.button("🚀 Start Interview", type="primary", use_container_width=True, disabled=start_disabled):
            st.session_state.position = position_input.strip()
            build_team(st.session_state.position)
            st.session_state.started = True
            st.session_state.history = []
            st.session_state.asked_questions = []
            st.session_state.rounds_done = 0
            st.session_state.next_comp_idx = 0
            add_history("system", f"Interview started for **{st.session_state.position}**.")

            comp = get_next_competency()
            task = ("Begin the interview briefly, then ask the FIRST QUESTION.\n"
                    f"- Target Competency this turn: **{comp}**\n"
                    "- Do not repeat previous question\n")
           
            msgs = run_turn(st.session_state.team, task=task)
            q = last_agent_messages(msgs, ["interviewer"]).get("interviewer", "").strip()
            if not q:
                q = "Welcome! To start, could you briefly introduce yourself?"
            st.session_state.asked_questions.append(q)
            add_history("interviewer", q)

    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            reset_all()
            st.rerun()

st.divider()
st.subheader("Score")
st.metric("Average Score", f"{st.session_state.avg_score:.2f}/10")
if st.session_state.scores:
    st.caption("Last Score JSON")
    st.code(json.dumps(st.session_state.scores[-1], indent=2))

render_history()

# =====================================
# MAIN INTERVIEW FLOW (UNCHANGED)
# =====================================
if st.session_state.started:
    user_text = st.chat_input("Your answer...")
    if user_text:
        add_history("user", user_text)
        st.session_state.rounds_done += 1

        # Coach responds
        msgs = run_turn(st.session_state.team, task=user_text)
        coach_text = last_agent_messages(msgs, ["coach"]).get("coach")
        if coach_text:
            add_history("coach", coach_text)

        # Scorer responds
        msgs = run_turn(st.session_state.team, task="Score the last answer now.")
        score_text = last_agent_messages(msgs, ["scorer"]).get("scorer")
        if score_text:
            parse_and_store_score(score_text)
            add_history("scorer", f"```json\n{score_text}\n```")

        # Interviewer asks next question
        comp = get_next_competency()
        previously_asked = "\n".join(st.session_state.asked_questions[-5:])

        interviewer_task = (
            f"Continue interview with the next question.\n"
            f"Target competency this turn: **{comp}**.\n"
            "- Do NOT repeat earlier questions; avoid similar phrasing.\n"
            f"- Previous questions:\n {previously_asked if previously_asked else 'None yet'}\n"
            "Prefer short, pointed questions tailored to the candidate’s last answer.\n"
        )

        msgs = run_turn(st.session_state.team, task=interviewer_task)
        next_q = last_agent_messages(msgs, ["interviewer"]).get("interviewer", "").strip()

        if next_q == "END" and st.session_state.rounds_done < 6:
            msg = run_turn(st.session_state.team, task=(
                "Do not end. Ask a follow-up interview question tailored to the previous answer. "
                "Avoid repeating earlier question; pick a new angle."
            ))
            next_q = last_agent_messages(msg, ["interviewer"]).get("interviewer", "").strip()

        if next_q == "END" and st.session_state.rounds_done >= 6:
            add_history("interviewer", "Thanks! The interview has concluded.")
            st.session_state.started = False
        else:
            if not next_q:
                next_q = f"Let's talk about {comp}, could you please share a concrete example from your experience?"
            st.session_state.asked_questions.append(next_q)
            add_history("interviewer", next_q)
