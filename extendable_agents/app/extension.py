"""Extension page."""

from aic_core.streamlit.tool_config import ToolConfigPage
from extendable_agents.constants import HF_REPO_ID


ToolConfigPage(HF_REPO_ID).run()
