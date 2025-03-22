from typing import Union
from unittest.mock import Mock
from unittest.mock import patch
import pytest
from huggingface_hub.errors import LocalEntryNotFoundError
from pydantic_ai import Agent
from pydantic_ai import Tool
from extendable_agents.agent import AgentConfig
from extendable_agents.agent import AgentFactory
from extendable_agents.agent import MCPServerStdio


def test_agent_config_initialization():
    """Test basic initialization of AgentConfig."""
    config = AgentConfig(
        model="openai:gpt-4o",
        name="TestAgent",
        system_prompt="Test prompt",
        retries=2,
    )

    assert config.model == "openai:gpt-4o"
    assert config.name == "TestAgent"
    assert config.system_prompt == "Test prompt"
    assert config.retries == 2
    assert config.hf_tools == []
    assert config.mcp_servers == []


@patch("extendable_agents.agent.HFRepo")
def test_from_hub(mock_hf_repo):
    """Test loading config from Hugging Face Hub."""
    # Create a Mock instance for the repo
    mock_repo = Mock()
    mock_hf_repo.return_value = mock_repo

    # Set up the load_config mock on the repo instance
    mock_repo.load_config.return_value = {
        "model": "openai:gpt-4o",
        "name": "TestAgent",
        "system_prompt": "Test prompt",
    }

    config = AgentConfig.from_hub("agent")

    assert config.model == "openai:gpt-4o"
    assert config.name == "TestAgent"
    assert config.system_prompt == "Test prompt"
    mock_repo.load_config.assert_called_with("agent")


@patch("extendable_agents.agent.HFRepo")
def test_push_to_hub(mock_hf_repo):
    """Test pushing config to Hugging Face Hub."""
    mock_repo = Mock()
    mock_hf_repo.return_value = mock_repo

    config = AgentConfig(model="openai:gpt-4o", name="TestAgent")

    config.push_to_hub()

    mock_repo.upload_content.assert_called_once()


@pytest.fixture
def basic_config():
    return AgentConfig(
        model="openai:gpt-4o",
        name="TestAgent",
        result_type=["str"],
        known_tools=["tool1"],
        hf_tools=["tool2"],
        mcp_servers=["command1 arg1 arg2", "command2"],
    )


@pytest.fixture
def agent_factory(basic_config):
    return AgentFactory(basic_config)


def test_init(basic_config):
    factory = AgentFactory(basic_config)
    assert factory.config == basic_config


@patch("extendable_agents.agent.load_tool")
def test_hf_to_pai_tools_local(mock_load_tool):
    # Setup mock tool
    def forward():
        """Test tool docstring"""
        pass

    mock_tool = Mock()
    mock_tool.forward = forward
    mock_tool.name = "test_tool"
    mock_tool.description = "test description"
    mock_load_tool.return_value = mock_tool

    tool = AgentFactory.hf_to_pai_tools("test_tool")
    assert isinstance(tool, Tool)
    assert tool.name == "test_tool"

    # Verify local_files_only was tried first
    mock_load_tool.assert_called_with(
        "test_tool", trust_remote_code=True, local_files_only=True
    )


@patch("extendable_agents.agent.load_tool")
def test_hf_to_pai_tools_remote(mock_load_tool):
    # First call raises LocalEntryNotFoundError, second call succeeds
    def forward():
        """Test tool docstring"""
        pass

    mock_load_tool.side_effect = [
        LocalEntryNotFoundError("Not found locally"),
        Mock(
            forward=forward,
            name="test_tool",
            description="test description",
            forward__doc__=None,
        ),
    ]

    tool = AgentFactory.hf_to_pai_tools("test_tool")
    assert isinstance(tool, Tool)
    assert mock_load_tool.call_count == 2


def test_get_result_type_empty(agent_factory):
    agent_factory.config.result_type = []
    assert agent_factory.get_result_type() == str  # noqa: E721


def test_get_result_type_single(agent_factory):
    agent_factory.config.result_type = ["str"]
    assert agent_factory.get_result_type() == str  # noqa: E721


@patch("extendable_agents.agent.HFRepo")
def test_get_result_type_structured_output(mock_hf_repo, agent_factory):
    # Setup mock for HFRepo
    mock_repo = Mock()
    mock_custom_type = type("CustomType", (), {})  # Creates a dynamic type
    mock_repo.load_structured_output.return_value = mock_custom_type
    mock_hf_repo.return_value = mock_repo

    # Test with a mix of built-in and custom types
    agent_factory.config.result_type = ["str", "custom_output_type"]
    result = agent_factory.get_result_type()

    # Verify HFRepo was called for custom type
    mock_repo.load_structured_output.assert_called_once_with("custom_output_type")

    # Verify the resulting Union type contains both str and our custom type
    assert result == Union.__getitem__((str, mock_custom_type))


@patch("extendable_agents.agent.HFRepo")
def test_get_tools(mock_hf_repo, agent_factory):
    # Setup mocks
    def example_tool():
        """Example tool docstring"""
        pass

    mock_repo = Mock()
    mock_repo.load_tool.return_value = example_tool
    mock_hf_repo.return_value = mock_repo

    with patch.object(AgentFactory, "hf_to_pai_tools") as mock_hf_to_pai:
        mock_hf_to_pai.return_value = Tool(example_tool, name="hf_tool")
        tools = agent_factory.get_tools()

        assert len(tools) == 2  # One known_tool and one hf_tool
        assert all(isinstance(tool, Tool) for tool in tools)


def test_get_mcp_servers(agent_factory):
    servers = agent_factory.get_mcp_servers()
    assert len(servers) == 2
    assert servers[0] == MCPServerStdio("command1", ["arg1", "arg2"])
    assert servers[1] == MCPServerStdio("command2", [])


@patch("extendable_agents.agent.OpenAIProvider")
def test_create_agent(mock_provider, agent_factory):
    # Setup mocks
    mock_provider_instance = Mock()
    mock_provider.return_value = mock_provider_instance

    with (
        patch.object(AgentFactory, "get_tools") as mock_get_tools,
        patch.object(AgentFactory, "get_result_type") as mock_get_result_type,
        patch.object(AgentFactory, "get_mcp_servers") as mock_get_mcp_servers,
    ):
        mock_get_tools.return_value = []
        mock_get_result_type.return_value = str
        mock_get_mcp_servers.return_value = []

        agent = agent_factory.create_agent("test-api-key")

        assert isinstance(agent, Agent)
        mock_provider.assert_called_once_with(api_key="test-api-key")
