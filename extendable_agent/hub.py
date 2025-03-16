"""Hub module for hosting tools."""

from github import Github
from github.ContentFile import ContentFile
from extendable_agent.constants import GITHUB_DIR
from extendable_agent.constants import GITHUB_REPO
from extendable_agent.constants import GITHUB_TOKEN


class ToolsHub:
    """Tools Hub class."""

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
