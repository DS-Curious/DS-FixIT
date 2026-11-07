
import streamlit as st

st.set_page_config(
    page_title="DS FixIT",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ DS FixIT")
st.caption("Your modular AI-powered assistant")

# Sidebar
st.sidebar.title("DS FixIT")
st.sidebar.subheader("AI Configuration")

provider = st.sidebar.selectbox(
    "Choose AI Provider",
    [
        "Not connected",
        "OpenAI",
        "Google Gemini",
        "Anthropic",
        "Custom API"
    ]
)

st.sidebar.write("Selected:", provider)

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Ask DS FixIT anything...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    response = (
        "DS FixIT received your message! "
        "AI integration is coming soon."
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.write(response)
