import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="gemma2-9b-it")

# Streamlit UI
st.set_page_config(page_title="📘 Multi-PDF Chatbot", layout="wide")
st.title("📘 Chat with Multiple PDFs using RAG")

# Sidebar for multiple PDF upload
st.sidebar.header("Upload PDFs")
uploaded_files = st.sidebar.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_docs = []

    # Process each uploaded PDF
    for uploaded_file in uploaded_files:
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        loader = PyPDFLoader(temp_file_path)
        docs = loader.load()
        all_docs.extend(docs)  # Combine all docs

    # Split all PDFs into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)

    # Embeddings & Vectorstore
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Prompt template
    template = """
    You are a helpful assistant that answers questions based on the given context.
    Context: {context}
    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    # Chat input/output
    st.subheader("💬 Ask a question about your PDFs")
    user_question = st.text_input("Enter your question here:")

    if user_question:
        result = qa_chain.invoke({"query": user_question})
        st.write("### 🤖 Answer:")
        st.write(result["result"])
