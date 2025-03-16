"""App state."""

from collections.abc import Callable
from functools import wraps
from typing import Any
from streamlit import session_state


class AppState:
    """Custom class for store all used session states."""

    def __init__(self) -> None:
        """Initialise all session states used in this app."""
        # Predefined states
        self.function_names: list[str] = []
        """Known function names."""
        self.selected_func_names: list[str] = []
        """Selected function names."""


def ensure_app_state(func: Callable) -> Callable:
    """Ensure app_state is initialised and pass it to the decorated function."""

    @wraps(func)
    def wrapper(*args: list, **kwargs: dict) -> Any:
        if "app_state" not in session_state:
            session_state.app_state = AppState()
        return func(session_state.app_state, *args, **kwargs)

    return wrapper
