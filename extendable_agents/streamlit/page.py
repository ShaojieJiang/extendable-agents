"""Streamlit page class."""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from streamlit import session_state


@dataclass
class PageStateSingleton:
    """App state. Singleton per session."""

    def __init__(self, file_path: str) -> None:
        """Initialize the page state."""
        self.file_path = file_path

    def __new__(cls, file_path: str) -> "PageStateSingleton":  # noqa: D102
        if file_path not in session_state:
            session_state[file_path] = super().__new__(cls)
        return session_state[file_path]


class AICPage(ABC):
    """AIC page."""

    @abstractmethod
    def run(self) -> None:
        """Run the page."""
        pass
