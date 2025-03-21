"""Agent module."""

from typing import TypeVar
from typing import Union
from huggingface_hub.errors import LocalEntryNotFoundError
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai import Tool
from smolagents import load_tool
from extendable_agents.hub import HFRepo


T = TypeVar("T")


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

    def get_result_type(self) -> type[T]:
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

        return Union[tuple(type_objects)]  # noqa: UP007

    def get_tools(self) -> list[Tool]:
        """Get the tools from known tools and hf tools."""
        tools = []
        hf_repo = HFRepo()
        for tool_name in self.config.known_tools:
            tool = hf_repo.load_tool(tool_name)
            tools.append(Tool(tool))
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
            model=self.config.model,
            result_type=result_type,
            system_prompt=self.config.system_prompt,
            name=self.config.name,
            model_settings=self.config.model_settings,
            retries=self.config.retries,
            result_tool_name=self.config.result_tool_name,
            result_tool_description=self.config.result_tool_description,
            result_retries=self.config.result_retries,
            tools=self.get_tools(),
            mcp_servers=self.get_mcp_servers(),
            defer_model_check=self.config.defer_model_check,
            end_strategy=self.config.end_strategy,
        )


class AgentModel:
    """Agent model."""

    def __init__(
        self,
        model: str = "openai:gpt-4o",
        name: str = "Agent",
        system_prompt: str = "You are a helpful assistant.",
        function_tools: list[str] | None = None,
        model_settings: dict | None = None,
        result_type: dict | None = None,
        mcp_servers: list[tuple[str, list[str]]] | None = None,
    ):
        """Initialize the agent model.

        Args:
            model (str): The model name.
            name (str): The name of the agent.
            system_prompt (str): The system prompt for the agent.
            function_tools (list[str]): The function tool names for the agent.
            model_settings (dict): The model settings for the agent.
            result_type (dict): The result type for the agent.
            mcp_servers (list[tuple[str, list[str]]]): The MCP servers for the agent.
        """
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.function_tools = function_tools
        self.model_settings = model_settings
        self.result_type = result_type
        self.mcp_servers = mcp_servers

    def get_pydantic_agent(self, model: str, hf_tools: list[Tool]) -> Agent:
        """Get the agent config from DB and convert to Pydantic agent."""
        return Agent(model=model, name=self.name, system_prompt=self.system_prompt)  # type: ignore[arg-type]
        # tools = []
        # if self.function_tools:
        #     tools_hub = ToolsHub()
        #     for tool_name in self.function_tools:
        #         function_code = tools_hub.get_file_from_github(tool_name)
        #         if not function_code:
        #             continue
        #         module = load_code_as_module(function_code)
        #         tools.append(getattr(module, tool_name))

        # model_settings = self.model_settings or {}

        # if self.mcp_servers:
        #     servers = [
        #         MCPServerStdio(command, args) for command, args in self.mcp_servers
        #     ]
        #     return Agent(
        #         model=model or self.model,  # type: ignore[arg-type]
        #         name=self.name,
        #         system_prompt=self.system_prompt,
        #         model_settings=ModelSettings(**model_settings),
        #         tools=tools + hf_tools,
        #         mcp_servers=servers,
        #     )
        # return Agent(
        #     model=model or self.model,  # type: ignore[arg-type]
        #     name=self.name,
        #     system_prompt=self.system_prompt,
        #     model_settings=ModelSettings(**model_settings),
        #     tools=tools + hf_tools,
        # )
