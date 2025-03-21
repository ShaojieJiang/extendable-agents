from collections.abc import Callable
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch
import pytest
from pydantic import BaseModel
from extendable_agents.constants import HF_TOKEN
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
    mock_snapshot.assert_called_once_with(
        repo_id="test-repo", repo_type="space", token=HF_TOKEN
    )


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


def test_upload_content():
    # Initialize the repo
    repo = HFRepo()

    test_cases = [
        # (filename, content, subdir, expected_extension)
        ("test_tool", "def test_tool(): pass", "tools", ".py"),
        (
            "test_model",
            "from pydantic import BaseModel\nclass test_model(BaseModel): pass",
            "pydantic_models",
            ".py",
        ),
        ("test_config", '{"key": "value"}', "agents", ".json"),
    ]

    for filename, content, subdir, extension in test_cases:
        with (
            patch("extendable_agents.hub.upload_file") as mock_upload,
            patch.object(HFRepo, "download_files") as mock_download,
        ):
            # Call the method
            repo.upload_content(filename, content, subdir)

            # Verify upload_file was called with correct arguments
            mock_upload.assert_called_once_with(
                path_or_fileobj=content.encode("utf-8"),
                path_in_repo=f"{subdir}/{filename}{extension}",
                repo_id=repo.repo_id,
                repo_type=repo.repo_type,
                commit_message=f"Update {filename}{extension}",
                token=HF_TOKEN,
            )

            # Verify download_files was called
            mock_download.assert_called_once()


def test_upload_content_invalid_subdir():
    repo = HFRepo()

    with pytest.raises(ValueError, match="Invalid type: invalid_dir"):
        repo.upload_content("test", "content", "invalid_dir")


def test_upload_content_with_extension():
    repo = HFRepo()

    with (
        patch("extendable_agents.hub.upload_file") as mock_upload,
    ):
        # Call with filename that already has extension
        repo.upload_content("test_tool.py", "content", "tools")

        # Verify correct handling of existing extension
        mock_upload.assert_called_once_with(
            path_or_fileobj=b"content",
            path_in_repo="tools/test_tool.py",
            repo_id=repo.repo_id,
            repo_type=repo.repo_type,
            commit_message="Update test_tool.py",
            token=HF_TOKEN,
        )


def test_list_files_existing_directory():
    """Test listing files in an existing directory."""
    with (
        patch("extendable_agents.hub.snapshot_download") as mock_snapshot,
        patch("os.path.exists") as mock_exists,
        patch("os.path.isdir") as mock_isdir,
        patch("os.listdir") as mock_listdir,
        patch("os.path.isfile") as mock_isfile,
    ):
        # Setup mocks
        mock_snapshot.return_value = "/fake/repo/path"
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file1.py", "file2.py", "file3.json"]
        mock_isfile.return_value = True

        hub = HFRepo()
        files = hub.list_files("tools")

        # Verify results
        assert files == ["file1", "file2", "file3"]
        mock_snapshot.assert_called_once_with(
            repo_id=hub.repo_id, repo_type=hub.repo_type, local_files_only=True
        )


def test_list_files_nonexistent_directory():
    """Test listing files in a non-existent directory."""
    with (
        patch("extendable_agents.hub.snapshot_download") as mock_snapshot,
        patch("os.path.exists") as mock_exists,
    ):
        mock_snapshot.return_value = "/fake/repo/path"
        mock_exists.return_value = False

        hub = HFRepo()
        files = hub.list_files("nonexistent")

        assert files == []


def test_list_files_not_a_directory():
    """Test listing files when path exists but is not a directory."""
    with (
        patch("extendable_agents.hub.snapshot_download") as mock_snapshot,
        patch("os.path.exists") as mock_exists,
        patch("os.path.isdir") as mock_isdir,
    ):
        mock_snapshot.return_value = "/fake/repo/path"
        mock_exists.return_value = True
        mock_isdir.return_value = False

        hub = HFRepo()
        files = hub.list_files("not_a_dir")

        assert files == []
