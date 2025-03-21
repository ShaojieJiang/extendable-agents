"""Hub module for hosting tools."""

import importlib
import json
import os
from collections.abc import Callable
from types import ModuleType
from typing import Literal
from huggingface_hub import hf_hub_download
from huggingface_hub import snapshot_download
from huggingface_hub import upload_file
from huggingface_hub.errors import LocalEntryNotFoundError
from pydantic import BaseModel
from extendable_agents.constants import HF_REPO_ID


HFRepoFileTypes = Literal["function", "config", "structured_output"]


class HFRepo:
    """Hugging Face Repo class.

    This class provides an interface to interact with Hugging Face repositories.
    It allows loading files, configs, and tools from a specified repository,
    as well as handling local caching when possible.
    """

    tools_dir: str = "tools"
    agents_dir: str = "agents"
    repo_type: str = "space"

    def __init__(self, repo_id: str = HF_REPO_ID) -> None:
        """Initialize the Hugging Face Hub."""
        self.repo_id = repo_id

    def download_files(self) -> None:
        """Download all files from the Hugging Face Hub."""
        snapshot_download(repo_id=self.repo_id, repo_type=self.repo_type)

    def get_file_path(self, filename: str, file_type: HFRepoFileTypes) -> str:
        """Get the local path to a file in the repo."""
        match file_type:
            case "function" | "structured_output":
                extension = ".py"
                subfolder = self.tools_dir
            case "config":
                extension = ".json"
                subfolder = self.agents_dir
            case _:
                raise ValueError(f"Invalid type: {file_type}")

        filename = self._check_extension(filename, extension)
        try:
            file_path = hf_hub_download(
                repo_id=self.repo_id,
                filename=filename,
                subfolder=subfolder,
                local_files_only=True,
                repo_type=self.repo_type,
            )
        except LocalEntryNotFoundError:
            file_path = hf_hub_download(
                repo_id=self.repo_id,
                filename=filename,
                subfolder=subfolder,
                repo_type=self.repo_type,
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

    def load_config(self, filename: str) -> dict:
        """Load a config from the Hugging Face Hub."""
        if not filename:
            return {}
        file_path = self.get_file_path(filename, "config")

        with open(file_path) as file:
            return json.load(file)

    def load_tool(self, filename: str) -> Callable | type[BaseModel] | None:
        """Load a tool from the Hugging Face Hub."""
        if not filename:
            return None
        name_without_extension = filename.split(".")[0]
        file_path = self.get_file_path(filename, "function")
        module = self._load_module(name_without_extension, file_path)
        func = getattr(module, name_without_extension)
        assert callable(func)

        return func

    def load_structured_output(self, filename: str) -> type[BaseModel] | None:
        """Load a structured output from the Hugging Face Hub."""
        if not filename:
            return None
        model = self.load_tool(filename)
        assert isinstance(model, type) and issubclass(model, BaseModel)

        return model

    def upload_content(
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
            path_or_fileobj=content.encode("utf-8"),
            path_in_repo=f"{path_in_repo}/{filename}",
            repo_id=self.repo_id,
            repo_type=self.repo_type,
            commit_message=f"Update {filename}",
        )
        self.download_files()  # Make sure local files are updated

    def list_files(self, subdir: str) -> list[str]:
        """List all files in the Hugging Face Hub."""
        repo_dir = snapshot_download(
            repo_id=self.repo_id, repo_type=self.repo_type, local_files_only=True
        )
        subdir_path = os.path.join(repo_dir, subdir)

        if not os.path.exists(subdir_path):
            return []

        if not os.path.isdir(subdir_path):
            return []

        return [
            f.split(".")[0]
            for f in os.listdir(subdir_path)
            if os.path.isfile(os.path.join(subdir_path, f))
        ]
