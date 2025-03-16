"""Streamlit app."""

import streamlit as st
from extendable_agent.constants import PAGES
from extendable_agent.hub import ToolsHub


def load_function_names() -> list[str]:
    """Load function names from Tools Hub."""
    tools_hub = ToolsHub()
    if "function_names" not in st.session_state:
        st.session_state.function_names = tools_hub.get_file_list_from_github()
    return st.session_state.function_names


def main() -> None:
    """Main function."""
    pg = st.navigation(PAGES)

    # Get function names from Tools Hub
    function_names = load_function_names()

    st.session_state.function_names = st.sidebar.multiselect(
        "Function or Pydantic model name",
        function_names,
    )
    pg.run()


main()
