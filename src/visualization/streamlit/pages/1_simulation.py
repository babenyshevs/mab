import os
import time
from typing import Dict, List, Tuple

import numpy as np
import streamlit as st

from src.data.reward_generator import RewardGenerator
from src.data.utilites import bootstrap
from src.general.io import read_yaml
from src.models.mab import MultiArmedBandit
from src.visualization.plots import get_bars, get_histograms, get_scatters
from src.visualization.streamlit.data import generate_data


def initialize_config() -> Dict:
    """Initialize the configuration from the YAML file.

    Returns:
        Dict: Configuration dictionary.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)).replace("pages", "")
    return read_yaml(f"{dir_path}default.yml")


def configure_controls(trials: int, mab_trials: int, arm_ids: List[str]) -> None:
    """Configure Streamlit sidebar controls.

    Args:
        trials (int): Number of trials per group.
        mab_trials (int): Total number of MAB trials.
        arm_ids (List[str]): List of arm identifiers.
    """
    st.sidebar.title("Controls")
    st.session_state["cfg"]["sleep_time"] = st.sidebar.radio(
        "Graph delay (seconds):", st.session_state["cfg"]["graph_delays"], horizontal=True
    )
    st.session_state["cfg"]["show_cumulative"] = st.sidebar.checkbox(
        "Show cumulative", value=st.session_state["cfg"]["show_cumulative"]
    )
    st.session_state["cfg"]["use_boostrap"] = st.sidebar.checkbox(
        "Use bootstrap", value=st.session_state["cfg"]["use_boostrap"]
    )

    st.sidebar.markdown("---")
    st.session_state["cfg"]["trials"]["value"] = st.sidebar.number_input(
        "Trials per group:",
        value=trials,
        min_value=st.session_state["cfg"]["trials"]["min"],
        max_value=st.session_state["cfg"]["trials"]["max"],
    )

    st.sidebar.write(
        f"""
        MAB trials: \n 
        - total: {mab_trials} \n 
        - explore: {int(mab_trials * st.session_state["cfg"]["mab_config"]["exploration_share"])} \n
        - exploit: {mab_trials - int(mab_trials * st.session_state["cfg"]["mab_config"]["exploration_share"])} \n
        """
    )
    st.sidebar.markdown("---")


def initialize_plots(
    arm_ids: List[str], reward_var_name: str, mab_trials: int
) -> Tuple[Dict, Dict, Dict, Dict, Dict, Dict]:
    """Initialize Plotly plots for the simulations.

    Args:
        arm_ids (List[str]): List of arm identifiers.
        reward_var_name (str): Name of the reward variable.
        mab_trials (int): Total number of MAB trials.

    Returns:
        Tuple[Dict, Dict, Dict, Dict, Dict, Dict]: Dictionaries for scatter, histogram, and bar plots, and Streamlit plot placeholders.
    """
    go_scatters, go_histograms, go_bars = {}, {}, {}
    st_scatters, st_histograms, st_bars = {}, {}, {}

    left_col, mid_col, right_col = st.columns(spec=[0.4, 0.3, 0.3], gap="large")

    for algorithm in st.session_state["cfg"]["algorithms"]:
        go_scatters[algorithm] = get_scatters(
            trace_ids=arm_ids,
            x_name=st.session_state["cfg"]["trial_variable"],
            y_name=reward_var_name,
            title=algorithm,
        )
        with left_col:
            st_scatters[algorithm] = st.empty()

        go_histograms[algorithm] = get_histograms(
            trace_ids=arm_ids, x_name=reward_var_name, title=algorithm
        )
        with mid_col:
            st_histograms[algorithm] = st.empty()

        go_bars[algorithm] = get_bars(
            trace_ids=arm_ids,
            x_name=st.session_state["cfg"]["trial_variable"],
            title=algorithm,
            max_y=mab_trials,
        )
        with right_col:
            st_bars[algorithm] = st.empty()

    return go_scatters, go_histograms, go_bars, st_scatters, st_histograms, st_bars


def update_plots(
    iter: int,
    data: Dict,
    arm_ids: List[str],
    trials: int,
    mab_trials: int,
    go_scatters: Dict,
    go_histograms: Dict,
    go_bars: Dict,
    st_scatters: Dict,
    st_histograms: Dict,
    st_bars: Dict,
    reward_var_name: str,
) -> None:
    """Update the plots with the current simulation data.

    Args:
        iter (int): Current iteration number.
        data (Dict): Dictionary containing simulation data.
        arm_ids (List[str]): List of arm identifiers.
        trials (int): Number of trials per group.
        mab_trials (int): Total number of MAB trials.
        go_scatters (Dict): Dictionary of scatter plots.
        go_histograms (Dict): Dictionary of histogram plots.
        go_bars (Dict): Dictionary of bar plots.
        st_scatters (Dict): Dictionary of Streamlit scatter plot placeholders.
        st_histograms (Dict): Dictionary of Streamlit histogram plot placeholders.
        st_bars (Dict): Dictionary of Streamlit bar plot placeholders.
        reward_var_name (str): Name of the reward variable.
    """
    total_y = {algorithm: 0 for algorithm in st.session_state["cfg"]["algorithms"]}
    total_trials = {algorithm: 0 for algorithm in st.session_state["cfg"]["algorithms"]}

    for trace, arm_id in enumerate(arm_ids):
        for alg_name, go_scatter in go_scatters.items():
            y = data[alg_name]["y"][arm_id][: iter + 1]
            y_cum = data[alg_name]["y_cumulative"][arm_id][: iter + 1]
            total_y[alg_name] += y_cum[-1]
            go_scatter.data[trace].x = list(range(0, iter))
            go_scatter.data[trace].y = y_cum if st.session_state["cfg"]["show_cumulative"] else y

        for alg_name, go_hist in go_histograms.items():
            y_array = np.array(data[alg_name]["y"][arm_id][: iter + 1])
            y_nozero = y_array[y_array != 0]
            if st.session_state["cfg"]["use_boostrap"]:
                y_nozero = bootstrap(y_nozero, repeats=trials)
            go_hist.data[trace].x = y_nozero

        for alg_name, go_bar in go_bars.items():
            try:
                y = data[alg_name]["trials_count_cumulative"][arm_id][iter]
                total_trials[alg_name] += y
            except IndexError:
                y = np.array(data[alg_name]["trials_count_cumulative"][arm_id][trials])
                total_trials[alg_name] = mab_trials
            go_bar.data[trace].x = [arm_id]
            go_bar.data[trace].y = [y]

    for alg_name, st_scatter in st_scatters.items():
        go_scatters[alg_name].update_layout(
            title=f"{alg_name}: achieved {reward_var_name} ({int(total_y[alg_name])})"
        )
        st_scatter.plotly_chart(
            go_scatters[alg_name],
            use_container_width=True,
        )

    for alg_name, st_histogram in st_histograms.items():
        st_histogram.plotly_chart(go_histograms[alg_name], use_container_width=True)

    for alg_name, st_bar in st_bars.items():
        go_bars[alg_name].update_layout(
            title=f"{alg_name}: total trials ({int(total_trials[alg_name])})"
        )
        st_bar.plotly_chart(go_bars[alg_name], use_container_width=True)


def main() -> None:
    """Main function to run the simulation and display results using Streamlit."""
    st.set_page_config(layout="wide")

    if "cfg" not in st.session_state:
        st.session_state["cfg"] = initialize_config()

    reward_var_name = st.session_state["cfg"]["reward_variable"]
    arm_ids = list(st.session_state["cfg"]["arms_config"].keys())
    trials = st.session_state["cfg"]["trials"]["value"]
    mab_trials = trials * len(arm_ids)

    configure_controls(trials, mab_trials, arm_ids)

    if st.sidebar.button("Start"):
        reward_generator = RewardGenerator(st.session_state["cfg"]["arms_config"])
        bandit = MultiArmedBandit(reward_generator, st.session_state["cfg"]["mab_config"])
        data = generate_data(
            st.session_state["cfg"]["trials"]["value"],
            st.session_state["cfg"]["mab_config"]["exploration_share"],
            st.session_state["cfg"]["algorithms"],
            arm_ids,
            reward_generator,
            bandit,
        )

        go_scatters, go_histograms, go_bars, st_scatters, st_histograms, st_bars = initialize_plots(
            arm_ids, reward_var_name, mab_trials
        )

        for iter in range(st.session_state["cfg"]["current_iteration"], mab_trials):
            update_plots(
                iter,
                data,
                arm_ids,
                trials,
                mab_trials,
                go_scatters,
                go_histograms,
                go_bars,
                st_scatters,
                st_histograms,
                st_bars,
                reward_var_name,
            )
            time.sleep(st.session_state["cfg"]["sleep_time"])

        st.session_state["cfg"]["current_iteration"] = 0


if __name__ == "__main__":
    main()
