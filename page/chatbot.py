"""Chatbot page."""

import os
from dataclasses import dataclass
import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest
from pydantic_ai.messages import ModelResponse
from pydantic_ai.messages import TextPart
from pydantic_ai.messages import UserPromptPart
from extendable_agent.agent import AgentModel


load_dotenv()


@dataclass
class ChatMessage:
    """Chat message."""

    role: str
    """Role of the message."""
    content: str
    """Content of the message."""


def init_chat_history() -> None:
    """Initialize chat history."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def get_response(user_input: str, agent: Agent) -> None:
    """Get response from agent."""
    history = [
        ModelRequest([UserPromptPart(content=chat.content)])
        if chat.role == "user"
        else ModelResponse([TextPart(content=chat.content)])
        for chat in st.session_state.chat_history
    ]
    st.session_state.chat_history.append(ChatMessage(role="user", content=user_input))
    st.chat_message("user").write(user_input)
    result = agent.run_sync(user_input, message_history=history)
    st.session_state.chat_history.append(
        ChatMessage(role="assistant", content=result.data)
    )


def display_chat_history() -> None:
    """Display chat history."""
    for chat in st.session_state.chat_history:
        st.chat_message(chat.role).write(chat.content)


def get_agent() -> Agent:
    """Get agent."""
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

    prompt = st.sidebar.text_area("Prompt", value="You are a helpful assistant.")
    model = st.sidebar.selectbox(
        "Model", options=["openai:gpt-4o-mini", "openai:gpt-4o"]
    )
    tools = st.session_state.function_names
    agent_model = AgentModel(
        model=model,
        name="Agent",
        system_prompt=prompt,
        function_tools=tools,
    )
    return agent_model.get_pydantic_agent(model)


def reset_chat_history() -> None:
    """Reset chat history."""
    st.session_state.chat_history = []


def main() -> None:
    """Main function."""
    st.title("Chatbot")
    init_chat_history()
    display_chat_history()
    agent = get_agent()
    st.sidebar.button("Reset chat history", on_click=reset_chat_history)
    user_input = st.chat_input("Enter a message")

    if user_input:
        get_response(user_input, agent)
        st.rerun()


main()
