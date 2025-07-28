from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_Key"),model_name="gpt-4.1",temperature=0.3)
qa_prompt = PromptTemplate(
input_variables=["role","jd"],
template = """
you are a senior technical interviewer.
Given this Job Role:{role}
coAnd this Job Decription: {jd}

Generate 5 **technical** mock interview Questions for this role.
Only include questions that test technical skills, knowledge or problem solving.
Do not include situationd or behavioral question.
For the each question provide a clear, strong sample answer.
Number them 1 to 5 and format like this:
1.Question: ... 
    Answer: ...
"""
)
qa_chain= LLMChain(llm=llm, prompt=qa_prompt)
st.title("Mock Interview Practice")
role = st.text_input("Job Role(e.g., Data Analyst)")
jd = st.text_area("Job Decription(paste here):")
if st.button("Generate Q&A"):
    if not role or not jd:
        st.warning("Please enter the both Role and JD")
    else:
        qa_paris = qa_chain.run({"role":role, "jd":jd})
        st.subheader("Mock Interview Q&A")
        st.write(qa_paris)
