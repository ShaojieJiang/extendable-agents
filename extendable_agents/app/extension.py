"""Extension page."""

import streamlit as st
from code_editor import code_editor
from pydantic import BaseModel
from extendable_agents.app.shared_components import function_selector
from extendable_agents.hub import HFRepo
from extendable_agents.tools import load_code_as_module


def edit_function(function_name: str) -> None:
    """Edit function."""
    hf_repo = HFRepo()
    if function_name:
        file_path = hf_repo.get_file_path(function_name, HFRepo.tools_dir)
        with open(file_path) as f:
            default_code = f.read()
    else:
        with open("extendable_agents/app/extension_template.py") as f:
            default_code = f.read()

    code = code_editor(default_code, lang="python", height=300, options={"wrap": True})

    if not code["text"]:
        st.warning(
            "Not saved. "
            "Press `Control + Enter` (Windows) or `Command + Enter` (Mac) to save."
        )
    function_name = st.text_input(
        "Function or Pydantic model name",
        value=function_name,
        disabled=not code["text"],
    )

    button_disabled = not function_name or not code["text"]
    if st.button("Save", disabled=button_disabled):
        # Test loading the code as a module
        if code["text"]:
            try:
                dynamic_module = load_code_as_module(code["text"])
                module_contents = [
                    item for item in dir(dynamic_module) if not item.startswith("__")
                ]
                assert function_name in module_contents
                func = getattr(dynamic_module, function_name)
                # Upload the code to Tools Hub
                if isinstance(func, type) and issubclass(func, BaseModel):
                    hf_repo.upload_content(
                        function_name, code["text"], HFRepo.pydantic_models_dir
                    )
                else:
                    hf_repo.upload_content(
                        function_name, code["text"], HFRepo.tools_dir
                    )
                st.success(f"Function `{function_name}` saved successfully!")
            except AssertionError:
                st.error(f"Definition `{function_name}` not found in module")
            except Exception as e:
                st.error(f"Error loading code as module: {str(e)}")
        else:
            st.write()


def main() -> None:
    """Main function."""
    st.title("Custom Function or Pydantic Model")
    functions = function_selector()
    selected_function = functions[0] if functions else ""
    edit_function(selected_function)


main()
