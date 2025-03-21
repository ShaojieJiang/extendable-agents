"""Chatbot page."""

import asyncio
import os
import streamlit as st
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest
from pydantic_ai.messages import ModelResponse
from pydantic_ai.messages import TextPart
from pydantic_ai.messages import UserPromptPart
from extendable_agents.agent import AgentConfig
from extendable_agents.agent import AgentFactory
from extendable_agents.app.app_state import AppState
from extendable_agents.app.app_state import ensure_app_state
from extendable_agents.app.shared_components import agent_selector
from extendable_agents.dataclasses import ChatMessage


def init_chat_history(app_state: AppState) -> None:
    """Initialize chat history."""
    if not app_state.chat_history:
        app_state.chat_history = []


async def get_response(app_state: AppState, user_input: str, agent: Agent) -> None:
    """Get response from agent."""
    history = [
        ModelRequest([UserPromptPart(content=chat.content)])
        if chat.role == "user"
        else ModelResponse([TextPart(content=chat.content)])
        for chat in app_state.chat_history
    ]
    app_state.chat_history.append(ChatMessage(role="user", content=user_input))
    st.chat_message("user").write(user_input)
    if agent._mcp_servers:
        async with agent.run_mcp_servers():
            result = await agent.run(user_input, message_history=history)  # type: ignore
    else:
        result = await agent.run(user_input, message_history=history)  # type: ignore
    app_state.chat_history.append(ChatMessage(role="assistant", content=result.data))


def display_chat_history(app_state: AppState) -> None:
    """Display chat history."""
    for chat in app_state.chat_history:
        st.chat_message(chat.role).write(chat.content)


def get_agent() -> Agent:
    """Get agent."""
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", "")
    )
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

    agent_name = agent_selector()
    agent_config = AgentConfig.from_hub(agent_name)
    agent_factory = AgentFactory(agent_config)
    agent = agent_factory.create_agent(api_key=openai_api_key)

    return agent


def reset_chat_history(app_state: AppState) -> None:
    """Reset chat history."""
    app_state.chat_history = []


@ensure_app_state
async def main(app_state: AppState) -> None:
    """Main function."""
    st.title("Extendable Agents")
    init_chat_history(app_state)
    display_chat_history(app_state)
    agent = get_agent()
    st.sidebar.button(
        "Reset chat history", on_click=reset_chat_history, args=(app_state,)
    )
    user_input = st.chat_input("Enter a message")

    if user_input:
        await get_response(app_state, user_input, agent)
        st.rerun()


asyncio.run(main())
