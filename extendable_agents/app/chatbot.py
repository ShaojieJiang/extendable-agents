"""Chatbot page."""

import os
import streamlit as st
from aic_core.agent.agent import AgentConfig
from aic_core.agent.agent import AgentFactory
from aic_core.streamlit.agent_page import AgentPage
from aic_core.streamlit.agent_page import PageState
from pydantic_ai import Agent
from extendable_agents.constants import HF_REPO_ID


class ChatbotPage(AgentPage):
    """Chatbot page."""

    def get_agent(self, agent_name: str) -> Agent:
        """Get agent."""
        openai_api_key = st.sidebar.text_input(
            "OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", "")
        )

        agent_config = AgentConfig.from_hub(self.repo_id, agent_name)
        agent_factory = AgentFactory(agent_config)
        agent = agent_factory.create_agent(api_key=openai_api_key)

        return agent


ChatbotPage(HF_REPO_ID, PageState(), "Extendable Agents").run()
