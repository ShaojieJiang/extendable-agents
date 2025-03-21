"""Agent module."""

from typing import Any
from typing import Union
from huggingface_hub.errors import LocalEntryNotFoundError
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai import Tool
from pydantic_ai.agent import ModelSettings
from smolagents import load_tool
from extendable_agents.hub import HFRepo


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
    known_tools: list[str] = []
    """List of known tools for the agent."""
    hf_tools: list[str] = []
    """List of Hugging Face tools for the agent."""
    mcp_servers: list[str] = []
    """List of MCP servers commands for the agent."""
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

        # Verify before uploading
        agent_factory = AgentFactory(self)
        agent_factory.create_agent()

        # Upload the file
        repo.upload_content(
            filename=self.name,
            content=self.model_dump_json(indent=2),
            subdir=HFRepo.agents_dir,
        )


class AgentFactory:
    """Factory class to create an agent from a config."""

    def __init__(self, config: AgentConfig):
        """Initialise the agent factory."""
        self.config = config

    @classmethod
    def hf_to_pai_tools(cls, tool_name: str) -> Tool:
        """Convert a Hugging Face tool to a Pydantic AI tool."""
        try:
            tool = load_tool(tool_name, trust_remote_code=True, local_files_only=True)
        except LocalEntryNotFoundError:
            tool = load_tool(tool_name, trust_remote_code=True)
        return Tool(
            tool.forward,
            name=tool.name,
            # Do nothing if the tool function already has a docstring
            description=tool.description if not tool.forward.__doc__ else None,
        )

    def get_result_type(self) -> Any:
        """Creates a Union type from a list of types."""
        if not self.config.result_type:
            return str
        if len(self.config.result_type) == 1:
            return eval(self.config.result_type[0])

        type_objects = []
        for type_str in self.config.result_type:
            # Handle built-in types and local class types
            if type_str in globals():
                type_objects.append(globals()[type_str])
            elif type_str in locals():
                type_objects.append(locals()[type_str])
            else:
                try:
                    type_objects.append(eval(type_str))
                except NameError:  # Structured output
                    hf_repo = HFRepo()
                    type_objects.append(hf_repo.load_structured_output(type_str))

        # Create a new type using Union
        return Union.__getitem__(tuple(type_objects))

    def get_tools(self) -> list[Tool]:
        """Get the tools from known tools and hf tools."""
        tools = []
        hf_repo = HFRepo()
        for tool_name in self.config.known_tools:
            tool = hf_repo.load_tool(tool_name)
            tools.append(Tool(tool))  # type: ignore[arg-type]
        for tool_name in self.config.hf_tools:
            tools.append(self.hf_to_pai_tools(tool_name))
        return tools

    def get_mcp_servers(self) -> list[tuple[str, list[str]]]:
        """Get the MCP servers from the config."""
        servers = []
        for server in self.config.mcp_servers:
            if not server.strip():
                continue
            command, *args = server.split()
            servers.append((command, args))
        return servers

    def create_agent(self) -> Agent:
        """Create an agent from a config."""
        result_type = self.get_result_type()
        return Agent(
            model=self.config.model,  # type: ignore[arg-type]
            result_type=result_type,
            system_prompt=self.config.system_prompt,
            name=self.config.name,
            model_settings=ModelSettings(**self.config.model_settings)
            if self.config.model_settings
            else None,
            retries=self.config.retries,
            result_tool_name=self.config.result_tool_name,
            result_tool_description=self.config.result_tool_description,
            result_retries=self.config.result_retries,
            tools=self.get_tools(),
            mcp_servers=self.get_mcp_servers(),  # type: ignore[arg-type]
            defer_model_check=self.config.defer_model_check,
            end_strategy=self.config.end_strategy,  # type: ignore[arg-type]
        )
