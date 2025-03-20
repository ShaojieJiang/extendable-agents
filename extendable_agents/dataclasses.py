"""Dataclasses."""

from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Chat message."""

    role: str
    """Role of the message."""
    content: str
    """Content of the message."""
