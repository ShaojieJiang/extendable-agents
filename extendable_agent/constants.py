"""Constants."""

import streamlit as st


PAGES = [
    st.Page("page/chatbot.py", title="Chatbot", icon="🤖"),
    st.Page("page/extension.py", title="Extension", icon="🔧"),
]
GITHUB_REPO = "AI-Colleagues/tools-hub"
GITHUB_DIR = "tools"
GITHUB_TOKEN = st.secrets["api_keys"]["TOOLS_HUB_TOKEN"]
