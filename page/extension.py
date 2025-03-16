"""Extension page."""

import streamlit as st
from code_editor import code_editor
from extendable_agent.hub import ToolsHub
from extendable_agent.tools import load_code_as_module


def edit_function(function_name: str) -> None:
    """Edit function."""
    tools_hub = ToolsHub()
    default_code = tools_hub.get_file_from_github(function_name)
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
                # Upload the code to Tools Hub
                tools_hub.upload_to_github(f"{function_name}.py", code["text"])
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
    functions = st.session_state.function_names
    selected_function = functions[0] if functions else ""
    edit_function(selected_function)


main()
