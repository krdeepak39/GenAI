import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

st.title("🦙 Chat with LLaMA2 (Ollama + LangChain)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# Input box for user
if prompt := st.chat_input("Ask me something..."):
    # Add user message to history
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Convert history into LangChain format
    formatted_history = [
        (m["role"], m["content"]) for m in st.session_state["messages"]
    ]

    # Build prompt
    chat_prompt = ChatPromptTemplate.from_messages(formatted_history)

    llm = Ollama(model="llama2")  # or "mistral"
    output_parse = StrOutputParser()
    chain = chat_prompt | llm | output_parse

    # Get model response
    response = chain.invoke({})

    # Save and display response
    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
