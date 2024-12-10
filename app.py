import os
import streamlit as st
from gradio_client import Client, handle_file

# Temporary directory for saving uploaded files
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# Gradio Client Initialization
client = Client("cvachet/pdf-chatbot")

def initialize_pdf_database(uploaded_files, chunk_size, chunk_overlap):
    try:
        st.info("Initializing PDF database...")
        file_paths = []
        for uploaded_file in uploaded_files:
            # Save file temporarily
            temp_file_path = os.path.join(TEMP_DIR, uploaded_file.name)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.read())
            file_paths.append(temp_file_path)

        # Use Gradio API to initialize the database
        result = client.predict(
            list_file_obj=[handle_file(file_path) for file_path in file_paths],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            api_name="/initialize_database",
        )
        st.success("PDF Database Initialized Successfully!")
        st.write(result)
    except Exception as e:
        st.error(f"Error during initialization: {str(e)}")

    finally:
        # Clean up temporary files
        for file_path in file_paths:
            os.remove(file_path)

def initialize_llm(llm_option, llm_temperature, max_tokens, top_k):
    try:
        st.info("Initializing LLM...")
        result = client.predict(
            llm_option=llm_option,
            llm_temperature=llm_temperature,
            max_tokens=max_tokens,
            top_k=top_k,
            api_name="/initialize_LLM",
        )
        st.success("LLM Initialized Successfully!")
        st.write(result)
    except Exception as e:
        st.error(f"Error during LLM initialization: {str(e)}")
        st.write("Full Error Details:")
        st.write(e.args)  # Output the detailed error message


def ask_question(message, history):
    try:
        st.info("Processing question...")
        result = client.predict(
            message=message,
            history=history,
            api_name="/conversation",
        )
        st.success("Response Received!")
        st.write(result[0])  # Display the response
    except Exception as e:
        st.error(f"Error during question processing: {str(e)}")

# Streamlit UI
st.title("Chat with PDF")
st.sidebar.header("Menu")

# Sidebar Options
with st.sidebar:
    st.subheader("PDF Database Initialization")
    uploaded_files = st.file_uploader(
        "Upload PDF Files", accept_multiple_files=True, type=["pdf"]
    )
    chunk_size = st.slider("Chunk Size", min_value=100, max_value=2000, value=600)
    chunk_overlap = st.slider("Chunk Overlap", min_value=0, max_value=100, value=40)

    if st.button("Initialize PDF Database"):
        if uploaded_files:
            initialize_pdf_database(uploaded_files, chunk_size, chunk_overlap)
        else:
            st.error("Please upload at least one PDF file.")

    st.subheader("LLM Initialization")
    llm_option = st.selectbox(
        "Select LLM Model",
        options=[
            'Mistral-7B-Instruct-v0.2', 'Mixtral-8x7B-Instruct-v0.1',
            'Mistral-7B-Instruct-v0.1', 'gemma-7b-it', 'gemma-2b-it',
            'zephyr-7b-beta', 'zephyr-7b-gemma-v0.1', 'Llama-2-7b-chat-hf',
            'phi-2', 'TinyLlama-1.1B-Chat-v1.0', 'mpt-7b-instruct',
            'falcon-7b-instruct', 'flan-t5-xxl'
        ],
        index=0
    )
    llm_temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7)
    max_tokens = st.slider("Max Tokens", min_value=256, max_value=2048, value=1024)
    top_k = st.slider("Top-K Samples", min_value=1, max_value=10, value=3)

    if st.button("Initialize LLM"):
        initialize_llm(llm_option, llm_temperature, max_tokens, top_k)

# Main Chat Section
st.subheader("Ask Questions from Your PDF")
user_question = st.text_input("Type your question here:")
if st.button("Submit Question"):
    if user_question:
        ask_question(user_question, history=[])
    else:
        st.error("Please enter a question.")
