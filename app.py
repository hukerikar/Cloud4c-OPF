import streamlit as st
from gradio_client import Client, handle_file

# Initialize Gradio Client
client = Client("cvachet/pdf-chatbot")

# Function to initialize PDF database
def initialize_pdf_database(uploaded_pdfs):
    pdf_files = [handle_file(pdf) for pdf in uploaded_pdfs]
    try:
        result = client.predict(
            list_file_obj=pdf_files,
            chunk_size=600,
            chunk_overlap=40,
            api_name="/initialize_database"
        )
        return result
    except Exception as e:
        st.error(f"Failed to initialize PDF database: {e}")
        return None

# Function to initialize LLM
def initialize_llm():
    try:
        result = client.predict(
            llm_option="Mistral-7B-Instruct-v0.2",
            llm_temperature=0.7,
            max_tokens=1024,
            top_k=3,
            api_name="/initialize_LLM"
        )
        return result
    except Exception as e:
        st.error(f"Failed to initialize LLM: {e}")
        return None

# Function to handle user conversation
def get_chat_response(user_message, history):
    try:
        result = client.predict(
            message=user_message,
            history=history,
            api_name="/conversation"
        )
        return result
    except Exception as e:
        st.error(f"Failed to get chatbot response: {e}")
        return None

# Main Streamlit application
def main():
    st.set_page_config(page_title="Chat with PDF", layout="wide")
    st.header("Chat with Your PDF")
    st.subheader("Upload PDFs, initialize the database, and ask questions.")

    # Sidebar for PDF Upload
    with st.sidebar:
        st.title("PDF Upload and Initialization")
        pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True, type=["pdf"])
        if st.button("Initialize PDF Database"):
            if pdf_docs:
                with st.spinner("Initializing PDF database..."):
                    db_result = initialize_pdf_database(pdf_docs)
                    if db_result:
                        st.success(f"Database initialized: {db_result}")
                    else:
                        st.error("PDF database initialization failed.")
            else:
                st.warning("Please upload at least one PDF file.")

        if st.button("Initialize LLM"):
            with st.spinner("Initializing LLM..."):
                llm_result = initialize_llm()
                if llm_result:
                    st.success(f"LLM initialized: {llm_result}")
                else:
                    st.error("LLM initialization failed.")

    # Chat Interface
    st.title("Chat Interface")
    user_message = st.text_input("Ask a question:")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("Submit Question"):
        if user_message.strip():
            with st.spinner("Getting response..."):
                chat_result = get_chat_response(user_message, st.session_state.chat_history)
                if chat_result:
                    # Extract chatbot response and update chat history
                    response, history = chat_result[0], chat_result[1]
                    st.session_state.chat_history.append((user_message, response))
                    st.write(f"Chatbot: {response}")
                else:
                    st.error("Failed to get chatbot response.")
        else:
            st.warning("Please enter a question.")

    # Display Chat History
    if st.session_state.chat_history:
        st.write("Chat History:")
        for user, bot in st.session_state.chat_history:
            st.write(f"**You**: {user}")
            st.write(f"**Bot**: {bot}")

if __name__ == "__main__":
    main()
