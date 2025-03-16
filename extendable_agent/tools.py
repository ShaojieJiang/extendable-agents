"""Tools module."""

import importlib.util
import sys
from types import ModuleType


def load_code_as_module(
    code_text: str, module_name: str = "dynamic_module"
) -> ModuleType:
    """Load code text as a Python module.

    Args:
        code_text (str): The Python code as a string
        module_name (str): Name to give the module

    Returns:
        module: The loaded Python module
    """
    # Create a module spec
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    assert spec

    # Create a new module based on the spec
    module = importlib.util.module_from_spec(spec)

    # Add the module to sys.modules
    sys.modules[module_name] = module

    # Execute the code within the module's namespace
    exec(code_text, module.__dict__)

    return module
