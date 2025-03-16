"""Chatbot page."""

import os
import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest
from pydantic_ai.messages import ModelResponse
from pydantic_ai.messages import TextPart
from pydantic_ai.messages import UserPromptPart
from extendable_agent.agent import AgentModel
from extendable_agent.app_state import AppState
from extendable_agent.app_state import ensure_app_state
from extendable_agent.dataclasses import ChatMessage


load_dotenv()


def init_chat_history(app_state: AppState) -> None:
    """Initialize chat history."""
    if not app_state.chat_history:
        app_state.chat_history = []


def get_response(app_state: AppState, user_input: str, agent: Agent) -> None:
    """Get response from agent."""
    history = [
        ModelRequest([UserPromptPart(content=chat.content)])
        if chat.role == "user"
        else ModelResponse([TextPart(content=chat.content)])
        for chat in app_state.chat_history
    ]
    app_state.chat_history.append(ChatMessage(role="user", content=user_input))
    st.chat_message("user").write(user_input)
    result = agent.run_sync(user_input, message_history=history)
    app_state.chat_history.append(ChatMessage(role="assistant", content=result.data))


def display_chat_history(app_state: AppState) -> None:
    """Display chat history."""
    for chat in app_state.chat_history:
        st.chat_message(chat.role).write(chat.content)


def get_agent(app_state: AppState) -> Agent:
    """Get agent."""
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", "")
    )
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

    prompt = st.sidebar.text_area("Prompt", value="You are a helpful assistant.")
    model = st.sidebar.selectbox(
        "Model", options=["openai:gpt-4o-mini", "openai:gpt-4o"]
    )
    tools = app_state.selected_func_names
    agent_model = AgentModel(
        model=model,
        name="Agent",
        system_prompt=prompt,
        function_tools=tools,
    )
    return agent_model.get_pydantic_agent(model)


def reset_chat_history(app_state: AppState) -> None:
    """Reset chat history."""
    app_state.chat_history = []


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main function."""
    st.title("Chatbot")
    init_chat_history(app_state)
    display_chat_history(app_state)
    agent = get_agent(app_state)
    st.sidebar.button(
        "Reset chat history", on_click=reset_chat_history, args=(app_state,)
    )
    user_input = st.chat_input("Enter a message")

    if user_input:
        get_response(app_state, user_input, agent)
        st.rerun()


main()
