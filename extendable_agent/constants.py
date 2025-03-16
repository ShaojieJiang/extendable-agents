"""Constants."""

import os
import streamlit as st


PAGES = [
    st.Page("page/chatbot.py", title="Chatbot", icon="🤖"),
    st.Page("page/extension.py", title="Extension", icon="🔧"),
]
FUNCTIONS_DIR = "./functions"
GITHUB_REPO = "AI-Colleagues/tools-hub"
GITHUB_TOKEN = os.getenv("TOOLS_HUB_TOKEN", "")
