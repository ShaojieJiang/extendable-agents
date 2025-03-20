"""Hugging Face Tools Hub."""

from pydantic_ai import Tool
from smolagents import load_tool


def hf_to_pai_tools(tool_name: str) -> Tool:
    """Convert a Hugging Face tool to a Pydantic AI tool."""
    tool = load_tool(tool_name, trust_remote_code=True)
    return Tool(
        tool.forward,
        name=tool.name,
        # Do nothing if the tool function already has a docstring
        description=tool.description if not tool.forward.__doc__ else None,
    )
