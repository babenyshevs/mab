import os

import streamlit as st

from src.general.io import read_yaml

st.set_page_config(layout="wide")

if "cfg" not in st.session_state:
    dir_path = os.path.dirname(os.path.realpath(__file__)).replace("pages", "")
    st.session_state["cfg"] = read_yaml(f"{dir_path}default.yml")


def display_active_strategy() -> None:
    """
    Display the active multi-armed bandit strategy and its parameters in the sidebar.
    """
    st.sidebar.write(
        f""" 
        active method: \n
        {st.session_state["cfg"]["mab_config"]["method"]} \n
        parameters:
        {st.session_state["cfg"]["mab_config"]["method_params"]}
        """
    )


def display_bandit_methods() -> dict:
    """
    Display options for selecting multi-armed bandit methods and their parameters.

    Returns:
        dict: A dictionary containing the selected method and its parameters.
    """
    new_mab_config = {}
    methods = st.session_state["cfg"]["mab_methods"]
    active_method = st.session_state["cfg"]["mab_config"]["method"]
    active_params = st.session_state["cfg"]["mab_config"]["method_params"]

    selected_method = st.radio(
        label="Select a MAB method",
        options=methods.keys(),
        index=list(methods.keys()).index(active_method),
    )

    selected_params = {}
    if selected_method == "epsilon_greedy":
        selected_params["epsilon"] = st.slider(
            "Epsilon",
            min_value=0.0,
            max_value=1.0,
            value=active_params.get("epsilon", methods["epsilon_greedy"]["epsilon"]),
        )
    elif selected_method == "softmax":
        selected_params["tau"] = st.slider(
            "Tau",
            min_value=0.01,
            max_value=1.0,
            value=active_params.get("tau", methods["softmax"]["tau"]),
        )
    elif selected_method == "ucb":
        selected_params["alpha"] = st.slider(
            "Alpha",
            min_value=0.0,
            max_value=10.0,
            value=active_params.get("alpha", methods["ucb"]["alpha"]),
        )

    new_mab_config["method"] = selected_method
    new_mab_config["method_params"] = selected_params

    new_mab_config["exploration_share"] = st.sidebar.number_input(
        "Share of exploration rounds, (0.01... 0.99):",
        value=st.session_state["cfg"]["mab_config"]["exploration_share"],
        min_value=0.01,
        max_value=0.99,
    )

    return new_mab_config


def update_configuration(new_config: dict) -> None:
    """
    Update the session state with the new configuration and display a success message.

    Args:
        new_config (dict): The new configuration for the arms.
    """
    st.session_state["cfg"]["mab_config"] = new_config
    st.sidebar.success("Bandit configuration updated!")
    display_active_strategy()


new_bandit_config = display_bandit_methods()

if st.sidebar.button("Update Configuration"):
    update_configuration(new_bandit_config)
