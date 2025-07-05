import streamlit as st

# -----------------------------
# 📝 Questions
# -----------------------------
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Paris", "London"],
        "answer": "Paris"
    },
    {
        "question": "2 + 2 = ?",
        "options": ["3", "4", "5"],
        "answer": "4"
    },
    {
        "question": "Which planet is the Red Planet?",
        "options": ["Earth", "Mars", "Venus"],
        "answer": "Mars"
    },
]

# -----------------------------
# ✅ Session state
# -----------------------------
if "score" not in st.session_state:
    st.session_state.score = 0

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

# -----------------------------
# ⚙️ Safe rerun helper
# -----------------------------
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# -----------------------------
# 🧩 Main logic
# -----------------------------
if st.session_state.q_index < len(questions):
    current_q = questions[st.session_state.q_index]

    st.write(f"**Question {st.session_state.q_index + 1} of {len(questions)}**")
    st.write(current_q["question"])

    user_answer = st.radio("Choose your answer:", current_q["options"])

    if st.button("Submit Answer"):
        if user_answer == current_q["answer"]:
            st.success("✅ Correct!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Incorrect! The correct answer is **{current_q['answer']}**.")

        st.session_state.q_index += 1
        safe_rerun()

else:
    st.write("---")
    st.success(f"🎉 Quiz completed! Your score: **{st.session_state.score} / {len(questions)}**")

    if st.button("Restart Quiz"):
        st.session_state.q_index = 0
        st.session_state.score = 0
        safe_rerun()
