"""Chatbot page."""

import json
import os
from typing import Any
import streamlit as st
from aic_core.agent.agent import AgentConfig, AgentFactory
from aic_core.streamlit.agent_page import AgentPage, PageState
from aic_core.streamlit.page import app_state
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequestPart,
    ModelResponsePart,
    TextPart,
    ToolReturnPart,
    UserPromptPart,
)
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

    def extract_tool_return_dict(self, part: ToolReturnPart) -> dict:
        """Extract tool return dict."""
        return json.loads(
            part.model_response_object()["return_value"]["content"][0]["text"]
        )

    def to_simple_messages(
        self, msg_parts: list[ModelRequestPart] | list[ModelResponsePart]
    ) -> list[tuple[str, str]]:
        """Convert message parts to simple messages."""
        result: list[tuple[str, Any]] = []
        for part in msg_parts:
            match part:
                case TextPart():
                    result.append((self.assistant_role, part.content))
                case UserPromptPart():
                    result.append((self.user_role, part.content))  # type: ignore
                case ToolReturnPart():
                    result.append(
                        (self.assistant_role, self.extract_tool_return_dict(part))
                    )
                case _:  # pragma: no cover
                    pass
        return result

    def display_chat_history(self) -> None:
        """Display chat history."""
        for msg in self.page_state.chat_history:
            simp_msgs = self.to_simple_messages(msg.parts)
            for simp_msg in simp_msgs:
                if isinstance(simp_msg[1], dict):
                    try:
                        with st.chat_message(simp_msg[0]):
                            comp_json = simp_msg[1]
                            comp_type = comp_json["type"]
                            comp_func = getattr(st, comp_type)
                            comp_func(**comp_json["kwargs"])
                    except Exception:  # pragma: no cover
                        st.chat_message(simp_msg[0]).write(simp_msg[1])
                else:
                    st.chat_message(simp_msg[0]).write(simp_msg[1])


ChatbotPage(HF_REPO_ID, ChatbotState(), "Extendable Agents").run()
