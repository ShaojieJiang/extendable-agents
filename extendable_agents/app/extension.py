"""Extension page."""

from aic_core.agent.agent_hub import AgentHub
from aic_core.streamlit.tool_config import ToolConfigPage
from extendable_agents.constants import HF_REPO_ID


class EAToolConfigPage(ToolConfigPage):
    """Tool Config Page."""

    def re_download_files(self) -> None:
        """Re-download files to local."""
        AgentHub(self.repo_id).download_files()


EAToolConfigPage(HF_REPO_ID).run()
