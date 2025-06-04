# ChatGPT-4.1 API

This project provides a simple Streamlit UI for interacting with the ChatGPT 4.1 model.

## Computer Use Mode

The interface now includes an optional **computer use** mode. When enabled in the
sidebar settings, ChatGPT can execute shell commands on your machine using the
`run_command` tool and display the output in the chat.

Use this mode with caution as it will run commands locally with the privileges
of the current user.
