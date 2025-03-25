"""Chatbot page."""

import asyncio
import os
import streamlit as st
from aic_core.agent.agent import AgentConfig
from aic_core.agent.agent import AgentFactory
from aic_core.streamlit.mixins import AgentSelectorMixin
from aic_core.streamlit.page import AICPage
from aic_core.streamlit.page import PageStateSingleton
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest
from pydantic_ai.messages import ModelResponse
from pydantic_ai.messages import TextPart
from pydantic_ai.messages import UserPromptPart
from extendable_agents.constants import HF_REPO_ID
from extendable_agents.dataclasses import ChatMessage


class PageState(PageStateSingleton):
    """Page state."""

    def __init__(self, __file__: str) -> None:
        """Initialize the page state."""
        super().__init__(__file__)
        self.chat_history: list[ChatMessage] = []


class ChatbotPage(AICPage, AgentSelectorMixin):
    """Chatbot page."""

    def __init__(self, repo_id: str) -> None:
        """Initialize the page."""
        super().__init__()
        self.repo_id = repo_id
        self.app_state = PageState(__file__)

    def init_chat_history(self) -> None:
        """Initialize chat history."""
        if not self.app_state.chat_history:
            self.app_state.chat_history = []

    async def get_response(self, user_input: str, agent: Agent) -> None:
        """Get response from agent."""
        history = [
            ModelRequest([UserPromptPart(content=chat.content)])
            if chat.role == "user"
            else ModelResponse([TextPart(content=chat.content)])
            for chat in self.app_state.chat_history
        ]
        self.app_state.chat_history.append(ChatMessage(role="user", content=user_input))
        st.chat_message("user").write(user_input)
        if agent._mcp_servers:
            async with agent.run_mcp_servers():
                result = await agent.run(user_input, message_history=history)  # type: ignore
        else:
            result = await agent.run(user_input, message_history=history)  # type: ignore
        self.app_state.chat_history.append(
            ChatMessage(role="assistant", content=result.data)
        )

    def display_chat_history(self) -> None:
        """Display chat history."""
        for chat in self.app_state.chat_history:
            st.chat_message(chat.role).write(chat.content)

    def get_agent(self) -> Agent:
        """Get agent."""
        openai_api_key = st.sidebar.text_input(
            "OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", "")
        )

        agent_name = self.agent_selector(self.repo_id)
        agent_config = AgentConfig.from_hub(self.repo_id, agent_name)
        agent_factory = AgentFactory(agent_config)
        agent = agent_factory.create_agent(api_key=openai_api_key)

        return agent

    def reset_chat_history(self) -> None:
        """Reset chat history."""
        self.app_state.chat_history = []

    async def main(self) -> None:
        """Main function."""
        st.title("Extendable Agents")
        self.init_chat_history()
        self.display_chat_history()
        agent = self.get_agent()
        st.sidebar.button("Reset chat history", on_click=self.reset_chat_history)
        user_input = st.chat_input("Enter a message")

        if user_input:
            await self.get_response(user_input, agent)
            st.rerun()

    def run(self) -> None:
        """Run the page."""
        asyncio.run(self.main())


ChatbotPage(HF_REPO_ID).run()
