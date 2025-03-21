from unittest.mock import Mock
from unittest.mock import patch
from extendable_agents.agent_config import AgentConfig
from extendable_agents.agent_config import MCPServerConfig


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
    assert config.tools == []
    assert config.mcp_servers == []


def test_mcp_server_config():
    """Test MCPServer configuration within AgentConfig."""
    mcp_config = MCPServerConfig(command="test_command", args=["arg1", "arg2"])

    config = AgentConfig(model="openai:gpt-4o", mcp_servers=[mcp_config])

    assert len(config.mcp_servers) == 1
    assert config.mcp_servers[0].command == "test_command"
    assert config.mcp_servers[0].args == ["arg1", "arg2"]


@patch("extendable_agents.agent_config.HFRepo")
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


@patch("extendable_agents.agent_config.HfApi")
def test_push_to_hub(mock_hf_api):
    """Test pushing config to Hugging Face Hub."""
    mock_api = Mock()
    mock_hf_api.return_value = mock_api

    config = AgentConfig(model="openai:gpt-4o", name="TestAgent")

    config.push_to_hub("test/repo")

    mock_api.upload_file.assert_called_once()
    args = mock_api.upload_file.call_args[1]
    assert args["path_in_repo"] == "agent.json"
    assert args["repo_id"] == "test/repo"
