"""Constants."""

import os
import streamlit as st


PAGES = [
    st.Page("extendable_agents/app/chatbot.py", title="Chatbot", icon="🤖"),
    st.Page("extendable_agents/app/agent.py", title="Custom Agent", icon="⚙️"),
    st.Page("extendable_agents/app/extension.py", title="Custom Extention", icon="🧩"),
]
HF_REPO_ID = os.environ.get("HF_REPO_ID", "NeuralNotwork/extendable-agents")
try:
    HF_TOKEN = st.secrets["api_keys"]["HF_TOKEN"]
except KeyError:
    HF_TOKEN = "hf_token"
