import streamlit as st


st.title(" shas.png ShasFinProp App")
name=st.text_input('Enter your name')
if st.button("Say Hi!"):
    if name:
        st.success(f"Hello {name}, Welcome to my page")
    else:
        st.warning("Please enter your sweet name")