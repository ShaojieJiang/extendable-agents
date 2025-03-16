"""Extension page."""

import os
import streamlit as st
from code_editor import code_editor
from extendable_agent.constants import FUNCTIONS_DIR
from extendable_agent.tools import load_code_as_module


def get_function_code(function_name: str) -> str:
    """Get function code."""
    try:
        with open(f"{FUNCTIONS_DIR}/{function_name}.py") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def edit_function(function_name: str) -> None:
    """Edit function."""
    default_code = get_function_code(function_name)
    code = code_editor(default_code, lang="python", height=300, options={"wrap": True})
    function_name = st.text_input(
        "Function or Pydantic model name", value=function_name
    )

    if st.button("Save", disabled=not function_name):
        # Test loading the code as a module
        if code["text"]:
            try:
                dynamic_module = load_code_as_module(code["text"])
                module_contents = [
                    item for item in dir(dynamic_module) if not item.startswith("__")
                ]
                assert function_name in module_contents
                # Save the code to a file in the functions directory
                # Ensure the functions directory exists
                os.makedirs(FUNCTIONS_DIR, exist_ok=True)

                # Write the code to the file
                with open(f"{FUNCTIONS_DIR}/{function_name}.py", "w") as f:
                    f.write(code["text"])

                st.success(f"Function {function_name} saved successfully!")
            except AssertionError:
                st.error(f"Definition {function_name} not found in module")
            except Exception as e:
                st.error(f"Error loading code as module: {str(e)}")
        else:
            st.write(
                "Press `Control + Enter` (Windows) or `Command + Enter` (Mac) "
                "after editing the function."
            )


def main() -> None:
    """Main function."""
    st.title("Edit Function")
    selected_function = st.session_state.function_name
    edit_function(selected_function)


main()
