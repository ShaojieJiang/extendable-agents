"""Constants."""

import os
import streamlit as st


PAGES = [
    st.Page("extendable_agents/app/chatbot.py", title="Chatbot", icon="🤖"),
    st.Page("extendable_agents/app/agent.py", title="Custom Agent", icon="⚙️"),
    st.Page("extendable_agents/app/extension.py", title="Custom Extention", icon="🧩"),
]
GITHUB_REPO = "AI-Colleagues/tools-hub"
GITHUB_DIR = "tools"
GITHUB_TOKEN = st.secrets["api_keys"]["TOOLS_HUB_TOKEN"]
HF_REPO_ID = os.environ.get("HF_REPO_ID", "NeuralNotwork/extendable-agents")
