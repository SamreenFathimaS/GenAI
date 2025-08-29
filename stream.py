import streamlit as st

# Title
st.title("Hello, Shas FinProp! 👋")

# Text
st.write("This is Shas Finance APP.")

# Input + Output
name = st.text_input("Enter your name:")
if st.button("Say Hello"):
    st.success(f"Hello, {name}! Welcome to Shas FinProp page")
