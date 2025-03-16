"""Hub module for hosting tools."""

from github import Github
from github.ContentFile import ContentFile
from extendable_agent.constants import GITHUB_REPO
from extendable_agent.constants import GITHUB_TOKEN


def upload_to_github(file_name: str, content: str) -> bool:
    """Upload a file to Tools Hub.

    Args:
        file_name (str): Path and name of the file to create in the repository.
        content (str): Content of the file to upload.
    """
    # Authenticate with GitHub using Personal Access Token
    g = Github(GITHUB_TOKEN)

    # Get the repository
    repo = g.get_repo(GITHUB_REPO)

    # Check if the file already exists in the repository
    try:
        existing_file = repo.get_contents(file_name)
        assert existing_file and isinstance(existing_file, ContentFile)
        # If it exists, update the file
        repo.update_file(
            path=existing_file.path,
            message=f"Update {file_name}",
            content=content,
            sha=existing_file.sha,
        )
        return True
    except Exception:
        # If it doesn't exist, create a new file
        repo.create_file(path=file_name, message=f"Add {file_name}", content=content)
        return True
