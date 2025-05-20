import os
import streamlit as st
from openai import OpenAI

# --- SETTINGS ---
MODEL = "gpt-4.1"
MAX_TOKENS = 32000
TEMPERATURE = 0.2

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ---- Custom CSS for darker sidebar and other tweaks ----
st.markdown("""
    <style>
    /* Make sidebar darker */
    section[data-testid="stSidebar"] {
        background-color: #16181c !important;
        color: #fff;
    }
    /* Make bar chart icon larger */
    .icon-style {
        font-size: 2rem;
        margin-right: 8px;
        vertical-align: middle;
    }
    .sidebar-title {
        font-size: 1.4rem;
        font-weight: bold;
        display: flex;
        align-items: center;
    }
    .sidebar-author {
        font-size: 1rem;
        color: #aaa;
        margin-bottom: 8px;
    }
    /* Main title bigger, RatGPT branding */
    .main-title {
        font-size: 2.6rem;
        font-weight: bold;
        color: #fff;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(
        '<div class="sidebar-title"><span class="icon-style">📊</span>RatGPT</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="sidebar-author">by BrownHo</div>', unsafe_allow_html=True)
    st.markdown(
        """
        - **Context window:** up to 1 million tokens  
        - **Model:** gpt-4.1  
        - [GitHub](https://github.com/openai/openai-python)
        """
    )
    with st.expander("⚙️ Settings", expanded=False):
        st.write("Current Model: ", MODEL)
        temp = st.slider("Temperature", 0.0, 1.0, TEMPERATURE, 0.05)
        max_tokens = st.slider("Max Response Tokens", 512, 32768, MAX_TOKENS, 512)
    if st.button("🧹 Clear chat history"):
        st.session_state.messages = [
            {"role": "system", "content": "You are RatGPT, a helpful assistant with a 1 million token context window."}
        ]
        st.experimental_rerun()

# --- Chat Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are RatGPT, a helpful assistant with a 1 million token context window."}
    ]

# --- MAIN PAGE ---
st.markdown('<div class="main-title">RatGPT</div>', unsafe_allow_html=True)

# Show conversation history (same as before)
st.markdown("""
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
""", unsafe_allow_html=True)

for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-row"><div class="user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="chat-row"><div class="ai-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)

user_input = st.chat_input("Ask anything...", key="input")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("RatGPT is thinking..."):
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

# To run this script, use the following command in your terminal:
# set
