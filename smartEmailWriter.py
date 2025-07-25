from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_Key"),model_name="gpt-4.1",temperature=0.5)
prompt = PromptTemplate(
input_variables=["bullet_points"],
template = """
you are a expert email writer.using the following bullet points drafta professional, friendly email:
{bullet_points}
Make sure the email has a greeting, clear, structure and a closing.
"""
)
chain= LLMChain(llm=llm, prompt=prompt)
st.title("Smart Email Writer")
st.write("Enter key bullet points for your email below:")
bullet_points = st.text_area("Bullet_points", height=200)
if st.button("Generate Email"):
    if bullet_points.strip()=="":
        st.warning("Please enter the some bullet points")
    else:
        email = chain.run({"bullet_points":bullet_points})
        st.subheader("Drafted Email")
        st.write(email)