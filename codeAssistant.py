from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_Key"),model_name="gpt-4.1",temperature=0.5)
prompt = PromptTemplate(
input_variables=["code_task"],
template = """
you are a professional code assistant help the user with the following task:
{code_task}
provide clean, well_commented code and explanation if needed.
"""
)
chain= LLMChain(llm=llm, prompt=prompt)
st.title("code Assistant")
code_task = st.text_area("Describe your coding task:")
if st.button("Generate Code"):
    if code_task.strip()=="":
        st.warning("Please entera task description")
    else:
        response = chain.run({"code_task":code_task})
        st.subheader("Assistant Response")
        st.code(response, language = 'python')