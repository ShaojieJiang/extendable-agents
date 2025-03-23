"""Main page."""

import streamlit as st
from aic_core.agent_hub import AgentHub
from extendable_agents.constants import HF_REPO_ID
from extendable_agents.constants import PAGES
from extendable_agents.logging import get_logger


logger = get_logger(__name__)


@st.cache_resource
def load_repo() -> None:
    """Load repo."""
    hf_repo = AgentHub(HF_REPO_ID)
    hf_repo.download_files()
    logger.info("Loaded repo")


def main() -> None:
    """Main function."""
    load_repo()
    pg = st.navigation(PAGES)

    pg.run()
