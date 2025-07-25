import streamlit as st 
from PyPDF2 import PdfReader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
import os

# Load environment variables
load_dotenv()

# Initialize the LLM and embeddings
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_Key"), model_name="gpt-4.1", temperature=0.2)
embeddings = OpenAIEmbeddings()

# Streamlit UI
st.title("RAG APP: Ask your PDF Anything")

# Upload PDF
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    raw_text = ""
    try:
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                raw_text += text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")

    if not raw_text.strip():
        st.error("Could not extract any text from this PDF.\n\n"
                 "It may be a scanned image PDF with no selectable text.\n\n"
                 "Please use a text-based PDF or run OCR (Optical Character Recognition) first.")
    else:
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(raw_text)

        if not chunks:
            st.error("No text chunks found. Nothing to embed.")
        else:
            st.success(f"Loaded! Split into {len(chunks)} chunks.")
            vector_store = FAISS.from_texts(chunks, embedding=embeddings)

            # Setup the RAG pipeline
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever()
            )

            # Input question
            query = st.text_input("Ask a question about your PDF:")
            if query:
                with st.spinner("Thinking..."):
                    answer = qa.run(query)
                    st.subheader("Answer")
                    st.write(answer)
