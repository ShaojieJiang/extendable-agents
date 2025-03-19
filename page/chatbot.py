"""Chatbot page."""

import asyncio
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
from extendable_agent.hf_tools import hf_to_pai_tools


load_dotenv()


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
            result = await agent.run(user_input, message_history=history)
    else:
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
        mcp_servers=app_state.mcp_servers,
    )
    hf_tools = list(app_state.tools.values())
    return agent_model.get_pydantic_agent(model, hf_tools)


def reset_chat_history(app_state: AppState) -> None:
    """Reset chat history."""
    app_state.chat_history = []


def get_hf_tools(app_state: AppState) -> None:
    """Get Hugging Face tool names."""
    user_input = st.sidebar.text_area(
        "Hugging Face tool names, one per line", value="", height=100
    )
    tool_names = [line.strip() for line in user_input.split("\n") if line.strip()]
    for tool_name in tool_names:
        try:
            tool = hf_to_pai_tools(tool_name)
            app_state.tools[tool.name] = tool
        except Exception as e:
            st.error(f"Error converting tool {tool_name}: {e}")


def config_mcp_servers(app_state: AppState) -> None:
    """Configure MCP server."""
    servers = st.sidebar.text_area(
        "MCP server commands and arguments, one per line",
        value="",
        height=100,
    )
    for server in servers.split("\n"):
        if not server.strip():
            continue
        command, *args = server.split()
        app_state.mcp_servers.append((command, args))


@ensure_app_state
async def main(app_state: AppState) -> None:
    """Main function."""
    st.title("Chatbot")
    get_hf_tools(app_state)
    config_mcp_servers(app_state)
    init_chat_history(app_state)
    display_chat_history(app_state)
    agent = get_agent(app_state)
    st.sidebar.button(
        "Reset chat history", on_click=reset_chat_history, args=(app_state,)
    )
    user_input = st.chat_input("Enter a message")

    if user_input:
        await get_response(app_state, user_input, agent)
        st.rerun()


asyncio.run(main())
