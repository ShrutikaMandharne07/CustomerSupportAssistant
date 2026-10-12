import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

SYSTEM_PROMPT = """You are a helpful e-commerce customer support assistant.
Be empathetic, concise, and clear. Ask for the details needed to understand an
issue. Never claim to have accessed an order, issued a refund, or taken an
account action. Explain general next steps, and direct the customer to the
store's support team when an action or store-specific policy must be confirmed.
Do not invent order details or policies.
"""


def create_chat_model(provider: str, model_name: str):
    if provider == "OpenRouter":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not set.")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model_name,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


def friendly_error(error: Exception, provider: str) -> str:
    detail = str(error).lower()
    if isinstance(error, ValueError) and "OPENROUTER_API_KEY" in str(error):
        return "Add OPENROUTER_API_KEY to your .env file and restart the app."
    status_code = getattr(error, "status_code", None)
    if provider == "OpenRouter" and (status_code == 402 or "insufficient credits" in detail):
        return "OpenRouter has no credits for this paid model. Choose openrouter/free or add credits to your account."
    if provider == "OpenRouter" and status_code == 403:
        return "OpenRouter denied access to this model. Choose a model enabled for your account."
    if provider == "OpenRouter" and status_code == 429:
        return "OpenRouter rate limit reached. Wait briefly, then try again."
    if any(term in detail for term in ("401", "unauthorized", "authentication", "api key")):
        return "Authentication failed. Check your OpenRouter API key in .env."
    if any(term in detail for term in ("404", "model", "not found")):
        return f"The model may be unavailable. Check the {provider} model name and access."
    if any(term in detail for term in ("connection", "connect", "timeout", "refused")):
        service = "Ollama" if provider == "Ollama" else "OpenRouter"
        return f"Could not connect to {service}. Check the service and configured URL."
    return "The assistant could not generate a reply. Check your provider settings and try again."


st.set_page_config(page_title="Customer Support Assistant", page_icon="💬")
st.title("Customer Support Assistant")
st.caption("An AI assistant for common e-commerce questions")

with st.sidebar:
    st.header("Model settings")
    providers = ("Ollama", "OpenRouter")
    default_provider = os.getenv("LLM_PROVIDER", "Ollama")
    provider = st.selectbox(
        "Provider",
        providers,
        index=providers.index(default_provider) if default_provider in providers else 0,
    )
    default_model = os.getenv(
        "OLLAMA_MODEL" if provider == "Ollama" else "OPENROUTER_MODEL",
        "llama3.2" if provider == "Ollama" else "openai/gpt-4o-mini",
    )
    model_name = st.text_input("Model", value=default_model)
    if st.button("Clear conversation", icon="🗑️"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("How can we help with your order?")
if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    history = [
        HumanMessage(content=message["content"])
        if message["role"] == "user"
        else AIMessage(content=message["content"])
        for message in st.session_state.messages[:-1]
    ]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    with st.chat_message("assistant"):
        try:
            chain = prompt | create_chat_model(provider, model_name)
            answer = chain.invoke({"history": history, "question": question})
            response = answer.content
            if not isinstance(response, str):
                response = str(response)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as error:
            st.error(friendly_error(error, provider))