"""Hub module for hosting tools."""

import importlib
import json
from collections.abc import Callable
from types import ModuleType
from typing import Literal
from github import Github
from github.ContentFile import ContentFile
from huggingface_hub import hf_hub_download
from huggingface_hub import snapshot_download
from huggingface_hub import upload_file
from huggingface_hub.errors import LocalEntryNotFoundError
from pydantic import BaseModel
from extendable_agents.constants import GITHUB_DIR
from extendable_agents.constants import GITHUB_REPO
from extendable_agents.constants import GITHUB_TOKEN


HFRepoFileTypes = Literal["function", "config", "structured_output"]


class HFRepo:
    """Hugging Face Repo class.

    This class provides an interface to interact with Hugging Face repositories.
    It allows loading files, configs, and tools from a specified repository,
    as well as handling local caching when possible.
    """

    tools_dir: str = "tools"
    agents_dir: str = "agents"

    def __init__(self, repo_id: str) -> None:
        """Initialize the Hugging Face Hub."""
        self.repo_id = repo_id

    def load_files(self) -> None:
        """Load all files from the Hugging Face Hub."""
        snapshot_download(repo_id=self.repo_id, repo_type="space")

    def _load_file(self, filename: str, file_type: HFRepoFileTypes) -> str:
        """Load a file from the Hugging Face Hub."""
        match file_type:
            case "function" | "structured_output":
                subfolder = self.tools_dir
            case "config":
                subfolder = self.agents_dir
            case _:  # pragma: no cover
                raise ValueError(f"Invalid type: {file_type}")
        try:
            file_path = hf_hub_download(
                repo_id=self.repo_id,
                filename=filename,
                subfolder=subfolder,
                local_files_only=True,
            )
        except LocalEntryNotFoundError:
            file_path = hf_hub_download(
                repo_id=self.repo_id, filename=filename, subfolder=subfolder
            )
        return file_path

    def _load_module(self, module_name: str, path: str) -> ModuleType:
        """Load a module from a path."""
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:  # pragma: no cover
            raise ImportError(f"Could not load spec for module {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _check_extension(self, filename: str, extension: str) -> str:
        """Check if the filename has the correct extension."""
        if not filename.endswith(extension):  # pragma: no cover
            filename = f"{filename}{extension}"
        return filename

    def load_config(self, filename: str, extension: str = ".json") -> dict:
        """Load a config from the Hugging Face Hub."""
        filename = self._check_extension(filename, extension)
        file_path = self._load_file(filename, "config")

        with open(file_path) as file:
            return json.load(file)

    def load_tool(
        self, filename: str, extension: str = ".py"
    ) -> Callable | type[BaseModel]:
        """Load a tool from the Hugging Face Hub."""
        name_without_extension = filename.split(".")[0]
        filename = self._check_extension(filename, extension)
        file_path = self._load_file(filename, "function")
        module = self._load_module(name_without_extension, file_path)
        func = getattr(module, name_without_extension)
        assert callable(func)

        return func

    def load_structured_output(
        self, filename: str, extension: str = ".py"
    ) -> type[BaseModel]:
        """Load a structured output from the Hugging Face Hub."""
        model = self.load_tool(filename, extension)
        assert isinstance(model, type) and issubclass(model, BaseModel)

        return model

    def upload_file(
        self,
        filename: str,
        content: str,
        file_type: HFRepoFileTypes,
    ) -> None:
        """Upload a file to the Hugging Face Hub."""
        match file_type:
            case "function" | "structured_output":
                extension = ".py"
                path_in_repo = self.tools_dir
            case "config":
                extension = ".json"
                path_in_repo = self.agents_dir
            case _:
                raise ValueError(f"Invalid type: {file_type}")

        filename = self._check_extension(filename, extension)

        upload_file(
            path_or_fileobj=content,
            path_in_repo=f"{path_in_repo}/{filename}",
            repo_id=self.repo_id,
            commit_message=f"Update {filename}",
        )


class ToolsHub:  # pragma: no cover
    """Tools Hub class. Deprecated."""

    def __init__(self) -> None:
        """Initialize the Tools Hub."""
        gh = Github(GITHUB_TOKEN)
        self.repo = gh.get_repo(GITHUB_REPO)

    def _add_extension(self, file_name: str) -> str:
        """Add .py extension to the file name if it is not present."""
        if not file_name.endswith(".py"):
            file_name = f"{file_name}.py"
        return file_name

    def _strip_extension(self, file_name: str) -> str:
        """Strip .py extension from the file name if it is present."""
        if file_name.endswith(".py"):
            file_name = file_name[:-3]
        return file_name

    def upload_to_github(self, file_name: str, content: str) -> bool:
        """Upload a file to Tools Hub.

        Args:
            file_name (str): Path and name of the file to create in the repository.
            content (str): Content of the file to upload.
        """
        file_name = self._add_extension(file_name)
        # Check if the file already exists in the repository
        full_path = f"{GITHUB_DIR}/{file_name}"
        try:
            existing_file = self.repo.get_contents(full_path)
            assert existing_file and isinstance(existing_file, ContentFile)
            # If it exists, update the file
            self.repo.update_file(
                path=existing_file.path,
                message=f"Update {file_name}",
                content=content,
                sha=existing_file.sha,
            )
            return True
        except Exception:
            # If it doesn't exist, create a new file
            self.repo.create_file(
                path=full_path, message=f"Add {file_name}", content=content
            )
            return True

    def get_file_from_github(self, file_name: str | None = None) -> str | None:
        """Get a file from Tools Hub.

        Args:
            file_name (str): Path and name of the file to get from the repository.
        """
        if not file_name:
            return None
        file_name = self._add_extension(file_name)
        full_path = f"{GITHUB_DIR}/{file_name}"
        file = self.repo.get_contents(full_path)
        assert file and isinstance(file, ContentFile)
        # Decode the base64-encoded content
        return file.decoded_content.decode("utf-8")

    def get_file_list_from_github(self) -> list[str]:
        """Get a list of files from Tools Hub.

        Returns:
            list[str]: List of file names.
        """
        files = self.repo.get_contents(GITHUB_DIR)
        assert files and isinstance(files, list)
        return [self._strip_extension(file.name) for file in files]
