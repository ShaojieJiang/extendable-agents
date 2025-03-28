"""Chatbot page."""

import os
import streamlit as st
from aic_core.agent.agent import AgentConfig
from aic_core.agent.agent import AgentFactory
from aic_core.streamlit.agent_page import AgentPage
from aic_core.streamlit.agent_page import PageState
from aic_core.streamlit.page import app_state
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from extendable_agents.constants import HF_REPO_ID


@app_state(__file__)
class ChatbotState(PageState):
    """Chatbot state."""

    chat_history: list[ModelMessage] = []


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


ChatbotPage(HF_REPO_ID, ChatbotState(), "Extendable Agents").run()
