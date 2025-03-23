"""Shared components."""

import streamlit as st
from aic_core.agent_hub import AgentHub
from extendable_agents.constants import HF_REPO_ID


def list_function_names() -> list[str]:
    """List function names from Tools Hub."""
    hf_repo = AgentHub(HF_REPO_ID)
    return hf_repo.list_files(AgentHub.tools_dir)


def function_selector() -> list[str]:
    """Function selector."""
    # Get function names from Tools Hub
    function_names = list_function_names()
    selected_function_names = st.sidebar.multiselect(
        "Function or Pydantic model name",
        function_names,
    )
    return selected_function_names


def list_agent_names() -> list[str]:
    """List all agents."""
    hf_repo = AgentHub(HF_REPO_ID)
    return hf_repo.list_files(AgentHub.agents_dir)


def agent_selector() -> str:
    """Agent selector."""
    agent_names = list_agent_names()
    return st.sidebar.selectbox("Agent", agent_names)
