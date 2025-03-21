from collections.abc import Callable
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch
import pytest
from huggingface_hub.errors import LocalEntryNotFoundError
from pydantic import BaseModel
from extendable_agents.hub import HFRepo


# Test fixtures and helper classes
class DummyModel(BaseModel):
    name: str
    value: int


def dummy_function():
    pass


@pytest.fixture
def hf_repo():
    return HFRepo("test-repo")


# Tests
def test_init():
    repo = HFRepo("test-repo")
    assert repo.repo_id == "test-repo"


@patch("extendable_agents.hub.snapshot_download")
def test_load_files(mock_snapshot):
    repo = HFRepo("test-repo")
    repo.download_files()
    mock_snapshot.assert_called_once_with(repo_id="test-repo", repo_type="space")


@patch("extendable_agents.hub.hf_hub_download")
def test_load_file(mock_download):
    repo = HFRepo("test-repo")
    mock_download.side_effect = ["/path/to/file"]

    result = repo.get_file_path("test.py", "function")
    assert result == "/path/to/file"
    mock_download.assert_called_with(
        repo_id="test-repo",
        filename="test.py",
        subfolder=HFRepo.tools_dir,
        local_files_only=True,
    )


@patch("extendable_agents.hub.hf_hub_download")
def test_load_file_fallback(mock_download):
    repo = HFRepo("test-repo")
    mock_download.side_effect = LocalEntryNotFoundError("Test exception")
    with pytest.raises(LocalEntryNotFoundError):
        repo.get_file_path("test.py", "function")


@patch("extendable_agents.hub.hf_hub_download")
def test_load_config(mock_download):
    repo = HFRepo("test-repo")
    mock_download.return_value = "config.json"

    with patch("builtins.open", mock_open(read_data='{"key": "value"}')):
        result = repo.load_config("config")
        assert result == {"key": "value"}


@patch("extendable_agents.hub.hf_hub_download")
@patch("extendable_agents.hub.importlib.util")
def test_load_tool(mock_importlib, mock_download):
    repo = HFRepo("test-repo")
    mock_download.return_value = "/path/to/tool.py"

    # Setup mock module
    mock_module = Mock()
    mock_module.tool = dummy_function
    mock_spec = Mock()
    mock_spec.loader = Mock()

    mock_importlib.spec_from_file_location.return_value = mock_spec
    mock_importlib.module_from_spec.return_value = mock_module

    result = repo.load_tool("tool")
    assert isinstance(result, Callable)


@patch("extendable_agents.hub.hf_hub_download")
@patch("extendable_agents.hub.importlib.util")
def test_load_structured_output(mock_importlib, mock_download):
    repo = HFRepo("test-repo")
    mock_download.return_value = "/path/to/model.py"

    # Setup mock module
    mock_module = Mock()
    mock_module.model = DummyModel
    mock_spec = Mock()
    mock_spec.loader = Mock()

    mock_importlib.spec_from_file_location.return_value = mock_spec
    mock_importlib.module_from_spec.return_value = mock_module

    result = repo.load_structured_output("model")
    assert issubclass(result, BaseModel)


@patch("extendable_agents.hub.upload_content")
def test_upload_content(mock_upload):
    repo = HFRepo("test-repo")

    # Test function upload
    repo.upload_content("test_func", "content", "function")
    mock_upload.assert_called_with(
        path_or_fileobj="content",
        path_in_repo=f"{HFRepo.tools_dir}/test_func.py",
        repo_id="test-repo",
        commit_message="Update test_func.py",
    )

    # Test config upload
    repo.upload_content("test_config", "content", "config")
    mock_upload.assert_called_with(
        path_or_fileobj="content",
        path_in_repo=f"{HFRepo.agents_dir}/test_config.json",
        repo_id="test-repo",
        commit_message="Update test_config.json",
    )


def test_upload_file_invalid_type():
    repo = HFRepo("test-repo")
    with pytest.raises(ValueError):
        repo.upload_content("test", "content", "invalid_type")  # type: ignore
