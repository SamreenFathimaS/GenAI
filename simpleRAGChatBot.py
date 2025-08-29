from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS   # ✅ FIXED import
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader

# Load API Key
load_dotenv()
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4.1", temperature=0.5)
embeddings = OpenAIEmbeddings()

# Streamlit UI
st.title("📄 RAG APP: Ask your PDF Anything")
uploaded_file = st.file_uploader("Upload your PDF documents", type=["pdf"])

if uploaded_file is not None:
    raw_text = ""
    try:
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                raw_text += text   # ✅ append all text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")

    if not raw_text.strip():
        st.error("Could not extract any text from this PDF.\n\n"
                 "It may be a scanned image PDF with no selectable text.\n\n"
                 "Please use a text-based PDF or run OCR first.")
    else:
        # ✅ Split text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(raw_text)

        if not chunks:
            st.error("No text chunks found, nothing to embed.")
        else:
            st.success(f"✅ Loaded! Split into {len(chunks)} chunks.")

            # ✅ Create Vector Store
            vector_store = FAISS.from_texts(chunks, embedding=embeddings)

            # ✅ Setup RetrievalQA
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever()
            )

            # ✅ User Question
            query = st.text_input("Ask a question about your PDF:")
            if query:
                with st.spinner("Thinking..."):
                    answer = qa.run(query)
                st.subheader("Answer")
                st.write(answer)
