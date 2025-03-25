"""Custom Agent."""

from aic_core.streamlit.agent_config import AgentConfigPage
from extendable_agents.constants import HF_REPO_ID


AgentConfigPage(HF_REPO_ID).run()
