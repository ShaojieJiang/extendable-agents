"""Streamlit app."""

import os
import streamlit as st
from extendable_agent.constants import FUNCTIONS_DIR
from extendable_agent.constants import PAGES


def main() -> None:
    """Main function."""
    st.navigation(PAGES)

    # Get files from ./functions directory
    function_names = []

    # Check if functions directory exists
    if os.path.exists(FUNCTIONS_DIR) and os.path.isdir(FUNCTIONS_DIR):
        # Get all Python files in the functions directory
        function_names = [
            f[:-3]
            for f in os.listdir(FUNCTIONS_DIR)
            if f.endswith(".py") and not f.startswith("__")
        ]

    st.session_state.function_name = st.sidebar.selectbox(
        "Function or Pydantic model name",
        function_names,
    )


main()
