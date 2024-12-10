import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    st.error("Google API Key not found. Please set the 'GOOGLE_API_KEY' in your environment.")
else:
    genai.configure(api_key=google_api_key)

# Function to extract text from uploaded PDF files
def get_pdf_text(pdf_docs):
    text = ""
    try:
        for pdf in pdf_docs:
            st.write(f"Processing file: {pdf.name}")  # Debug log
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        if not text.strip():
            raise ValueError("No text could be extracted from the uploaded PDF files.")
    except Exception as e:
        st.error("Error during PDF text extraction.")
        st.error(traceback.format_exc())
    return text

# Function to split text into chunks
def get_text_chunks(text):
    try:
        st.write("Splitting text into chunks...")  # Debug log
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        if not chunks:
            raise ValueError("No valid chunks created from the text.")
        st.write(f"Total chunks created: {len(chunks)}")  # Debug log
    except Exception as e:
        st.error("Error during text chunking.")
        st.error(traceback.format_exc())
        chunks = []
    return chunks

# Function to create a vector store using embeddings
def get_vector_store(text_chunks):
    try:
        st.write("Creating embeddings and vector store...")  # Debug log
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
        st.write("Vector store saved successfully.")  # Debug log
    except Exception as e:
        st.error("Error during vector store creation.")
        st.error(traceback.format_exc())

# Function to create a conversational chain
def get_conversational_chain():
    try:
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not in
        provided context, just say, "Answer is not available in the context." Do not provide the wrong answer.

        Context:
        {context}?

        Question:
        {question}

        Answer:
        """
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        return chain
    except Exception as e:
        st.error("Error during conversational chain setup.")
        st.error(traceback.format_exc())
        return None

# Function to handle user questions
def user_input(user_question):
    try:
        st.write("Loading vector store...")  # Debug log
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        new_db = FAISS.load_local("faiss_index", embeddings)
        docs = new_db.similarity_search(user_question)
        chain = get_conversational_chain()
        if chain:
            response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
            st.write("Reply: ", response["output_text"])
    except Exception as e:
        st.error("Error during question processing.")
        st.error(traceback.format_exc())

# Main Streamlit application
def main():
    st.set_page_config(page_title="Cloud4c OPF Chatbot", layout="wide")
    st.header("Cloud4c OPF Chatbot")
    st.subheader("Upload PDFs and ask questions based on their content.")

    user_question = st.text_input("Ask a Question from the PDF Files")

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True, type=["pdf"])
        if st.button("Submit & Process"):
            try:
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    if raw_text.strip():
                        text_chunks = get_text_chunks(raw_text)
                        if text_chunks:
                            get_vector_store(text_chunks)
                            st.success("Processing complete!")
                        else:
                            st.error("No valid chunks created from the text.")
                    else:
                        st.error("No valid text extracted from the PDF.")
            except Exception as e:
                st.error("Error during processing.")
                st.error(traceback.format_exc())

if __name__ == "__main__":
    main()
