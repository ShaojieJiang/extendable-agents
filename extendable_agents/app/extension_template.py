"""Template for custom function or Pydantic model."""

from pydantic import BaseModel
from pydantic import Field


class MyModel(BaseModel):
    """My model."""

    attr1: str = Field(..., description="The first attribute.")
    attr2: int = Field(..., description="The second attribute.")


def my_function(arg1: int, arg2: int) -> int:
    """My function. Docstrings and arguments are useful for function calls.

    Args:
        arg1: The first argument.
        arg2: The second argument.
    """
    return arg1 + arg2
