"""Main page."""

import streamlit as st
from extendable_agents.constants import PAGES
from extendable_agents.hub import HFRepo
from extendable_agents.logging import get_logger


logger = get_logger(__name__)


@st.cache_resource
def load_repo() -> None:
    """Load repo."""
    hf_repo = HFRepo()
    hf_repo.download_files()
    logger.info("Loaded repo")


def main() -> None:
    """Main function."""
    load_repo()
    pg = st.navigation(PAGES)

    pg.run()
