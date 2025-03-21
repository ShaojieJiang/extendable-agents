"""Agent config."""

from pydantic import BaseModel
from extendable_agents.hub import HFRepo
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
    def from_hub(cls, agent_name: str) -> "AgentConfig":
        """Load an agent config from Hugging Face Hub."""
        repo = HFRepo()
        config_obj = repo.load_config(agent_name)
        return cls(**config_obj)

    def push_to_hub(self) -> None:
        """Upload a JSON file to Hugging Face Hub."""
        repo = HFRepo()

        # Upload the file
        repo.upload_content(
            filename=self.name,
            content=self.model_dump_json(),
            file_type="config",
        )
