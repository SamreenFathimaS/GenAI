import streamlit as st
import asyncio
from typing import Dict, List, Any
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# -------------------------------
# Initialize session state safely
# -------------------------------
def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "scores" not in st.session_state:
        st.session_state.scores = {}
    if "asked_question" not in st.session_state:
        st.session_state.asked_question = []
    if "model_client" not in st.session_state:
        st.session_state.model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    if "team" not in st.session_state:
        # Create interviewer + user agent
        interviewer = AssistantAgent(
            name="Interviewer",
            system_message="You are a professional interviewer. Ask one question at a time.",
            model_client=st.session_state.model_client
        )
        candidate = UserProxyAgent(
            name="Candidate",
            system_message="You are the candidate being interviewed.",
        )
        st.session_state.team = RoundRobinGroupChat([interviewer, candidate])


# -------------------------------
# Run a conversation turn
# -------------------------------
async def _run_turn_async(team: RoundRobinGroupChat, task: Dict[str, Any], timeout_sec: int = 60):
    return await asyncio.wait_for(team.step(task), timeout=timeout_sec)

def run_turn(team: RoundRobinGroupChat, task: Dict[str, Any], timeout_sec: int = 60):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(_run_turn_async(team, task, timeout_sec))
        else:
            return loop.run_until_complete(_run_turn_async(team, task, timeout_sec))
    except RuntimeError:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop.run_until_complete(_run_turn_async(team, task, timeout_sec))


# -------------------------------
# Streamlit App UI
# -------------------------------
st.set_page_config(page_title="AI Interviewer", layout="wide")
st.title("🤖 AI Interviewer")

init_session_state()

position = st.text_input("Enter the Job Position:")
if st.button("Start Interview"):
    if position:
        intro_msg = f"You are a professional interviewer for the role: {position}. Start the interview by asking the first question."
        st.session_state.history.append({"role": "system", "content": intro_msg})

        task = {"input": intro_msg}
        msgs = run_turn(st.session_state.team, task)

        if msgs:
            for msg in msgs:
                st.session_state.history.append({"role": msg.source, "content": msg.content})


# -------------------------------
# Chat Interface
# -------------------------------
st.subheader("Interview Progress")

# Display history
for h in st.session_state.history:
    st.write(f"**{h['role']}**: {h['content']}")

# Input box for candidate answer
user_input = st.text_input("Your answer:", key="user_input")

if user_input:
    # Save answer
    st.session_state.history.append({"role": "user", "content": user_input})

    # Send to interviewer team
    task = {"input": user_input}
    msgs = run_turn(st.session_state.team, task)

    # Append interviewer response
    if msgs:
        for msg in msgs:
            if msg.source != "user":
                st.session_state.history.append({"role": msg.source, "content": msg.content})

    # Clear input
    st.session_state.user_input = ""


# -------------------------------
# Sidebar Debug Info
# -------------------------------
with st.sidebar:
    st.subheader("Session Debug Info")
    st.json(st.session_state.scores)
    st.json(st.session_state.history)
