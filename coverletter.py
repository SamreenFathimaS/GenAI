from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import PyPDF2


load_dotenv()
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_Key"),model_name="gpt-4.1",temperature=0.3)
cover_letter_prompt = PromptTemplate(
input_variables=["resume_textts","job_title","company"],
template = """
you are a expert career coach and writer.write a professional, personalized cover letter for this role:
Job_itle:{job_title}
company: {company}
Use the following resume information:
{resume_text}
Keep the tone formal but friendly highlight relevant experience and enthusiasm for the role.
"""
)
cover_letter_chain= LLMChain(llm=llm, prompt=cover_letter_prompt)
st.title("Cover Letter Generation")
uploaded_file = st.file_uploader("upload your resume(PDF or TXT)", type=(["pdf", "txt"]))
job_title = st.text_input("Tob.title(eg.,software Engineer)")
Company = st.text_input("company Name(optional)")
if st.button("Generate cover letter"):                                 
    if not uploaded_file or not job_title:
        st,Warning("Please upload your resume and enter the job title.")
    else:
        if uploaded_file.name.endswith(".txt"):
            resume_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            resume_text = " "
            for Page in pdf_reader.pages:
                resume_text += Page.extract_text()
        else:
            st.error("unsupported file type")
            resume_text = " "
        if resume_text:
            cover_letter = cover_letter_chain({"resume_text":resume_text,
                                               "job_title":job_title,
                                               "company":Company if Company else "the company"})
                  
        st.subheader("Generated Cover Letter")
        st.write(cover_letter)