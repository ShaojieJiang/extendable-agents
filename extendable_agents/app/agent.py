"""Custom Agent."""

from aic_core.agent.agent_hub import AgentHub
from aic_core.streamlit.agent_config import AgentConfigPage
from extendable_agents.constants import HF_REPO_ID


class EAConfigPage(AgentConfigPage):
    """Agent Config Page."""

    def re_download_files(self) -> None:
        """Re-download files to local."""
        AgentHub(self.repo_id).download_files()


EAConfigPage(HF_REPO_ID).run()
