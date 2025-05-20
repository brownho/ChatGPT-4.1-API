import os
import streamlit as st
from openai import OpenAI

# --- SETTINGS ---
MODEL = "gpt-4.1"  # 1M context as of 2024
MAX_TOKENS = 32000
TEMPERATURE = 0.2

# --- API KEY SETUP ---
API_KEY = "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" 
if not API_KEY:
    st.error("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
    st.stop()
client = OpenAI(api_key=API_KEY)

# --- Streamlit UI Config ---
st.set_page_config(
    page_title="ChatGPT 4.1 UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- SIDEBAR ---
st.sidebar.title("🗂️ ChatGPT 4.1")
st.sidebar.markdown(
    """
    - **Context window:** up to 1 million tokens
    - **Model:** gpt-4.1
    - [GitHub](https://github.com/openai/openai-python)
    """
)

# Set defaults
temp = TEMPERATURE
max_tokens = MAX_TOKENS

with st.sidebar.expander("⚙️ Settings", expanded=False):
    st.write("Current Model: ", MODEL)
    temp = st.slider("Temperature", 0.0, 1.0, TEMPERATURE, 0.05)
    max_tokens = st.slider("Max Response Tokens", 512, 32768, MAX_TOKENS, 512)

# --- Chat Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are ChatGPT, a helpful assistant with a 1 million token context window."}
    ]

# --- MAIN CHAT WINDOW ---

st.title("ChatGPT 4.1")
st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #005555;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px;
        margin: 4px 0 8px 80px;
        max-width: 700px;
        display: inline-block;
    }
    .ai-bubble {
        background-color: #222225;
        color: #fff;
        border-radius: 18px 18px 18px 4px;
        padding: 12px;
        margin: 4px 80px 8px 0;
        max-width: 700px;
        display: inline-block;
    }
    .chat-row {
        display: flex;
        align-items: flex-start;
        margin-bottom: 2px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Show conversation history
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-row"><div class="user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="chat-row"><div class="ai-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)

# --- Chat Input ---
user_input = st.chat_input("Ask anything...", key="input")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("ChatGPT is thinking..."):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages,
                max_tokens=max_tokens,
                temperature=temp,
                stream=False,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.experimental_rerun()

# --- Clear Chat Button ---
if st.sidebar.button("🧹 Clear chat history"):
    st.session_state.messages = [
        {"role": "system", "content": "You are ChatGPT, a helpful assistant with a 1 million token context window."}
    ]
    st.experimental_rerun()
