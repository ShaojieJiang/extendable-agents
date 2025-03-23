"""Custom Agent."""

from typing import get_args
import streamlit as st
from aic_core.agent import AgentConfig
from aic_core.agent_hub import AgentHub
from pydantic_ai.models import KnownModelName
from extendable_agents.app.shared_components import agent_selector
from extendable_agents.app.shared_components import list_function_names
from extendable_agents.constants import HF_REPO_ID


def list_result_type_options() -> list[str]:
    """List all result types."""
    primitive_types = ["str", "int", "float", "bool"]
    hf_repo = AgentHub(HF_REPO_ID)
    return primitive_types + hf_repo.list_files(AgentHub.pydantic_models_dir)


def configure(config: AgentConfig) -> AgentConfig:
    """Widgets to configure the agent."""
    model_options = [
        model for model in get_args(KnownModelName) if model.startswith("openai")
    ]
    model = st.selectbox(
        "Select a model",
        model_options,
        index=model_options.index(config.model),
    )

    result_type_options = list_result_type_options()
    result_type = st.multiselect(
        "Result type",
        options=result_type_options,
        default=config.result_type,
    )
    system_prompt = st.text_area("System prompt", value=config.system_prompt)
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=config.model_settings.get("temperature", 1.0)
        if config.model_settings
        else 1.0,
    )
    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=config.model_settings.get("top_p", 1.0) if config.model_settings else 1.0,
    )
    model_settings = {
        "temperature": temperature,
        "top_p": top_p,
    }
    retries = st.number_input(
        "Retries", min_value=0, max_value=100, value=config.retries
    )
    result_tool_name = st.text_input("Result tool name", value=config.result_tool_name)
    result_tool_description = st.text_area(
        "Result tool description", value=config.result_tool_description
    )
    result_retries = st.number_input(
        "Result retries", min_value=0, max_value=100, value=config.retries
    )
    list_known_tools = list_function_names()
    default_known_tools = [
        tool for tool in config.known_tools if tool in list_known_tools
    ]
    known_tools = st.multiselect(
        "Known tools", options=list_known_tools, default=default_known_tools
    )
    hf_tools = st.text_area("HF tools", value="\n".join(config.hf_tools))
    mcp_servers = st.text_area("MCP servers", value="\n".join(config.mcp_servers))
    defer_model_check = st.toggle("Defer model check", value=config.defer_model_check)
    end_strategy = st.selectbox("End strategy", ["early", "exhaustive"])
    name = st.text_input("Name", value="Agent")

    return AgentConfig(
        model=model,
        result_type=result_type,
        system_prompt=system_prompt,
        model_settings=model_settings,
        retries=retries,
        result_tool_name=result_tool_name,
        result_tool_description=result_tool_description,
        result_retries=result_retries,
        known_tools=known_tools,
        hf_tools=[x for x in hf_tools.split("\n") if x],
        mcp_servers=[x for x in mcp_servers.split("\n") if x],
        defer_model_check=defer_model_check,
        end_strategy=end_strategy,
        name=name,
        repo_id=HF_REPO_ID,
    )


def main() -> None:
    """Main function."""
    st.title("Custom Agent")
    agent_name = agent_selector()
    if agent_name:
        config = AgentConfig.from_hub(HF_REPO_ID, agent_name)
    else:  # Initialize a new agent
        config = AgentConfig(model="openai:gpt-4o", repo_id=HF_REPO_ID)
    new_config = configure(config)
    st.write(new_config)
    if st.button("Save", on_click=new_config.push_to_hub):
        st.success("Agent pushed to the hub.")


main()
