"""Main page."""

import streamlit as st
from extendable_agents.app.app_state import AppState
from extendable_agents.app.app_state import ensure_app_state
from extendable_agents.constants import PAGES
from extendable_agents.hub import HFRepo
from extendable_agents.logging import get_logger


logger = get_logger(__name__)


# @st.cache_resource  # TODO:
def load_repo() -> None:
    """Load repo."""
    hf_repo = HFRepo()
    hf_repo.download_files()
    logger.info("Loaded repo")


def load_function_names(app_state: AppState) -> list[str]:
    """Load function names from Tools Hub."""
    if not app_state.function_names:
        hf_repo = HFRepo()
        app_state.function_names = hf_repo.list_files(HFRepo.tools_dir)
    return app_state.function_names


def function_selector(app_state: AppState) -> None:
    """Function selector."""
    # Get function names from Tools Hub
    function_names = load_function_names(app_state)
    selected_function_names = st.sidebar.multiselect(
        "Function or Pydantic model name",
        function_names,
    )
    app_state.selected_func_names = selected_function_names


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main function."""
    load_repo()
    pg = st.navigation(PAGES)

    function_selector(app_state)
    pg.run()
