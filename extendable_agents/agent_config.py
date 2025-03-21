"""Agent config."""

import json
from huggingface_hub import HfApi
from huggingface_hub.errors import LocalEntryNotFoundError
from pydantic import BaseModel
from extendable_agents.logging import get_logger


logger = get_logger(__name__)


class MCPServerConfig(BaseModel):
    """MCPServer config."""

    command: str
    args: list[str]


class AgentConfig(BaseModel):
    """Configuration class for Agent initialization."""

    model: str
    """Model name. Must be a valid pydantic_ai.models.KnownModelName."""
    result_type: list[str] = ["str"]
    """Result type. Can be name of Python primitives or a list of HF Hub file names."""
    system_prompt: str = "You are a helpful assistant."
    """System prompt for the agent."""
    # deps_type: type[AgentDepsT] = (NoneType,)
    name: str = "Agent"
    """Name of the agent."""
    model_settings: dict | None = None
    """Model settings for the agent."""
    retries: int = 1
    """Number of retries for the agent."""
    result_tool_name: str = "final_result"
    """Name of the result tool."""
    result_tool_description: str | None = None
    """Description of the result tool."""
    result_retries: int | None = None
    """Number of retries for the result tool."""
    tools: list[str] = []
    """List of tools for the agent."""
    mcp_servers: list[MCPServerConfig] = []
    """List of MCP servers for the agent."""
    defer_model_check: bool = False
    """Whether to defer model check for the agent."""
    end_strategy: str = "early"
    """End strategy for the agent."""
    config_version: str = "0.0.1"
    """Version of the agent config."""

    @classmethod
    def from_hub(cls, repo_id: str) -> "AgentConfig":
        """Load an agent config from Hugging Face Hub."""
        api = HfApi()
        try:
            config_str = api.hf_hub_download(
                repo_id=repo_id, filename="agent.json", local_files_only=True
            )
        except LocalEntryNotFoundError as e:
            logger.warning(f"Failed to load agent config from Hugging Face Hub: {e}")
            config_str = api.hf_hub_download(repo_id=repo_id, filename="agent.json")
        config_obj = json.loads(config_str)
        return cls(**config_obj)

    def push_to_hub(self, repo_id: str) -> None:
        """Upload a JSON file to Hugging Face Hub."""
        api = HfApi()

        # Upload the file
        api.upload_file(
            path_or_fileobj=self.model_dump_json(),
            path_in_repo="agent.json",
            repo_id=repo_id,
        )
