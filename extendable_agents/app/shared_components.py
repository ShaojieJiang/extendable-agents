"""Shared components."""

import streamlit as st
from extendable_agents.hub import HFRepo


def list_function_names() -> list[str]:
    """List function names from Tools Hub."""
    hf_repo = HFRepo()
    return hf_repo.list_files(HFRepo.tools_dir)


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
    hf_repo = HFRepo()
    return hf_repo.list_files(HFRepo.agents_dir)


def agent_selector() -> str:
    """Agent selector."""
    agent_names = list_agent_names()
    return st.sidebar.selectbox("Agent", agent_names)
