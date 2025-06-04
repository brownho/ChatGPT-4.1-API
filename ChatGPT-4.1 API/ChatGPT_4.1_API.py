import os
import json
import subprocess
import io
import zipfile
import streamlit as st
from openai import OpenAI

# --- SETTINGS ---
MODEL = "gpt-4.1"  # 1M context as of 2024
MAX_TOKENS = 32000
TEMPERATURE = 0.2

# --- LOCAL COMMAND EXECUTION ---
def run_command(command: str) -> str:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        return output.strip() if output else "(no output)"
    except Exception as e:
        return f"Error running command: {e}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command on the local machine and return its output.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "Command to execute"}},
                "required": ["command"],
            },
        },
    }
]

# --- Power BI Processing ---
def process_pbix(pbix_bytes: bytes) -> dict:
    """Extract key JSON files from a PBIX archive."""
    result = {}
    try:
        with zipfile.ZipFile(io.BytesIO(pbix_bytes)) as zf:
            for name in zf.namelist():
                lower = name.lower()
                if lower.endswith("datamodelschema"):
                    result["DataModelSchema"] = json.loads(
                        zf.read(name).decode("utf-8", errors="ignore")
                    )
                elif lower.endswith("metadata"):
                    result["Metadata"] = json.loads(
                        zf.read(name).decode("utf-8", errors="ignore")
                    )
                elif lower.endswith("report/layout") or lower.endswith("layout"):
                    result["Layout"] = json.loads(
                        zf.read(name).decode("utf-8", errors="ignore")
                    )
    except Exception as e:
        result["error"] = str(e)
    return result

# --- API KEY SETUP ---
API_KEY = os.environ.get("OPENAI_API_KEY")
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

if "computer_mode" not in st.session_state:
    st.session_state.computer_mode = False

with st.sidebar.expander("⚙️ Settings", expanded=False):
    st.write("Current Model: ", MODEL)
    temp = st.slider("Temperature", 0.0, 1.0, TEMPERATURE, 0.05)
    max_tokens = st.slider("Max Response Tokens", 512, 32768, MAX_TOKENS, 512)
    st.session_state.computer_mode = st.checkbox(
        "Enable computer use", value=st.session_state.computer_mode
    )

# --- Chat Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are ChatGPT, a helpful assistant with a 1 million token context window. "
                "When computer use is enabled you may run shell commands using the `run_command` tool."
            ),
        }
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

# --- Power BI Upload ---
pbix_file = st.sidebar.file_uploader("Upload Power BI .pbix", type=["pbix"])
if pbix_file:
    with st.spinner("Processing PBIX..."):
        pbix_data = process_pbix(pbix_file.getvalue())
        st.session_state.pbix_json = json.dumps(pbix_data, indent=2)

if "pbix_json" in st.session_state:
    st.subheader("Extracted PBIX JSON")
    st.download_button(
        "Download JSON",
        st.session_state.pbix_json,
        file_name="pbix.json",
        mime="application/json",
    )
    st.text_area("PBIX JSON Preview", st.session_state.pbix_json, height=300)
    if st.button("Send PBIX JSON to ChatGPT"):
        st.session_state.messages.append(
            {
                "role": "user",
                "content": f"PBIX JSON:\n```json\n{st.session_state.pbix_json}\n```",
            }
        )
        st.experimental_rerun()

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
            if st.session_state.computer_mode:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=st.session_state.messages,
                    max_tokens=max_tokens,
                    temperature=temp,
                    tools=TOOLS,
                    tool_choice="auto",
                )
                message = response.choices[0].message
                while message.tool_calls:
                    for call in message.tool_calls:
                        if call.function.name == "run_command":
                            args = json.loads(call.function.arguments)
                            output = run_command(args.get("command", ""))
                            st.session_state.messages.append(
                                {
                                    "role": "function",
                                    "name": "run_command",
                                    "content": output,
                                }
                            )
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=st.session_state.messages,
                        max_tokens=max_tokens,
                        temperature=temp,
                    )
                    message = response.choices[0].message
                answer = message.content
            else:
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
        {
            "role": "system",
            "content": (
                "You are ChatGPT, a helpful assistant with a 1 million token context window. "
                "When computer use is enabled you may run shell commands using the `run_command` tool."
            ),
        }
    ]
    st.experimental_rerun()
