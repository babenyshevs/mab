import os

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.general.io import read_yaml

st.set_page_config(layout="wide")

# Initialize configuration if not already in session state
if "cfg" not in st.session_state:
    dir_path = os.path.dirname(os.path.realpath(__file__)).replace("pages", "")
    st.session_state["cfg"] = read_yaml(f"{dir_path}default.yml")


def display_arm_configuration() -> dict:
    """
    Display the configuration options for each arm in the left column.

    This function creates an expander for all arms, where the user can select
    the distribution type (gauss or uniform) and set the corresponding parameters
    (mean and std for gauss, lower and upper bounds for uniform).

    Returns:
        dict: A dictionary containing the updated configuration for all arms.
    """
    new_arms_config = {}
    i = 0
    with st.expander("Distributions", expanded=True):
        columns = st.columns(spec=len(st.session_state["cfg"]["arms_config"]), gap="large")
        for arm_id, config in st.session_state["cfg"]["arms_config"].items():
            with columns[i]:
                dist = st.radio(
                    label=arm_id,
                    options=["gauss", "uniform"],
                    index=["gauss", "uniform"].index(config["distribution"]),
                    key=f"dist_{arm_id}",
                    horizontal=True,
                )
                if dist == "gauss":
                    mean = st.number_input(
                        "Mean",
                        value=config["params"][0],
                        key=f"mean_{arm_id}",
                    )
                    std = st.number_input(
                        "Standard Deviation",
                        value=config["params"][1],
                        key=f"std_{arm_id}",
                    )
                    new_arms_config[arm_id] = {
                        "distribution": dist,
                        "params": [mean, std],
                    }
                elif dist == "uniform":
                    lower = st.number_input(
                        "Lower Bound",
                        value=config["params"][0],
                        key=f"low_{arm_id}",
                    )
                    upper = st.number_input(
                        "Upper Bound",
                        value=config["params"][1],
                        key=f"up_{arm_id}",
                    )
                    new_arms_config[arm_id] = {
                        "distribution": dist,
                        "params": [lower, upper],
                    }
            i += 1
    return new_arms_config


def plot_distributions(distributions: dict) -> None:
    """
    Plot all distributions on the same graph using Plotly.

    Args:
        distributions (dict): The configuration for all arms.
    """
    fig = go.Figure()
    for arm_id, config in distributions.items():
        dist = config["distribution"]
        params = config["params"]
        if dist == "gauss":
            mean, std = params
            x = np.linspace(mean - 4 * std, mean + 4 * std, 1000)
            y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=arm_id))
        elif dist == "uniform":
            lower, upper = params
            x = np.linspace(lower - 1, upper + 1, 1000)
            y = np.where((x >= lower) & (x <= upper), 1 / (upper - lower), 0)
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=arm_id))

    fig.update_layout(title="True distributions", xaxis_title="Value", yaxis_title="Density")
    st.plotly_chart(fig, use_container_width=True)


def update_configuration(new_config: dict) -> None:
    """
    Update the session state with the new configuration and display a success message.

    Args:
        new_config (dict): The new configuration for the arms.
    """
    st.session_state["cfg"]["arms_config"] = new_config
    st.sidebar.success("Reward configuration updated!")
    st.write(st.session_state["cfg"]["arms_config"])


def reset_to_defaults() -> None:
    """
    Reset the configuration to the default settings and display a success message.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)).replace("pages", "")
    st.session_state["cfg"]["arms_config"] = read_yaml(f"{dir_path}default.yml")["arms_config"]
    st.sidebar.success("Reverted to defaults!")
    st.write(st.session_state["cfg"]["arms_config"])


# Display arm configuration in the left column
new_arms_config = display_arm_configuration()

# Plot all distributions in the right column
plot_distributions(new_arms_config)

# Sidebar buttons for updating configuration and resetting to defaults
if st.sidebar.button("Update Configuration"):
    update_configuration(new_arms_config)

if st.sidebar.button("Reset to defaults"):
    reset_to_defaults()
