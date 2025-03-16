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

    def upload_to_github(self, file_name: str, content: str) -> bool:
        """Upload a file to Tools Hub.

        Args:
            file_name (str): Path and name of the file to create in the repository.
            content (str): Content of the file to upload.
        """
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

    def get_file_from_github(self, file_name: str) -> str:
        """Get a file from Tools Hub.

        Args:
            file_name (str): Path and name of the file to get from the repository.
        """
        full_path = f"{GITHUB_DIR}/{file_name}"
        file = self.repo.get_contents(full_path)
        assert file and isinstance(file, ContentFile)
        return file.content

    def get_file_list_from_github(self) -> list[str]:
        """Get a list of files from Tools Hub.

        Returns:
            list[str]: List of file names.
        """
        files = self.repo.get_contents(GITHUB_DIR)
        assert files and isinstance(files, list)
        return [file.name for file in files]
