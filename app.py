"""Streamlit app."""

import streamlit as st


PAGES = [
    st.Page("pages/chatbot.py", title="Chatbot"),
    st.Page("pages/extension.py", title="Extension"),
]


def main() -> None:
    """Main function."""
    st.navigation(PAGES)


main()
