# Initialize RewardGenerator and MultiArmedBandit
import os
import time

import numpy as np
import streamlit as st

from src.data.reward_generator import RewardGenerator
from src.data.utilites import bootstrap
from src.general.io import read_yaml
from src.models.mab import MultiArmedBandit
from src.visualization.plots import get_bars, get_histograms, get_scatters
from src.visualization.streamlit.data import generate_data

st.set_page_config(layout="wide")

if "cfg" not in st.session_state:
    dir_path = os.path.dirname(os.path.realpath(__file__)).replace("pages", "")
    st.session_state["cfg"] = read_yaml(f"{dir_path}default.yml")

# assign some configurations to variables to shorten the code
reward_var_name = st.session_state["cfg"]["reward_variable"]
arm_ids = list(st.session_state["cfg"]["arms_config"].keys())
trials = st.session_state["cfg"]["trials"]["value"]
mab_trials = trials * len(arm_ids)  # because in MAB only 1 arm is pulled per trial

# CONTROLS
st.sidebar.title("Controls")
sleep_time = st.sidebar.radio(
    "Graph delay (seconds):", st.session_state["cfg"]["graph_delays"], horizontal=True
)
st.session_state["cfg"]["show_cumulative"] = st.sidebar.checkbox(
    "Show cumulative", value=st.session_state["cfg"]["show_cumulative"]
)
st.session_state["cfg"]["use_boostrap"] = st.sidebar.checkbox(
    "Use bootstrap", value=st.session_state["cfg"]["use_boostrap"]
)

st.sidebar.markdown("""---""")
st.session_state["cfg"]["trials"]["value"] = st.sidebar.number_input(
    "Trials per group:",
    value=trials,
    min_value=st.session_state["cfg"]["trials"]["min"],
    max_value=st.session_state["cfg"]["trials"]["max"],
)

if st.sidebar.button("Reset trials"):
    st.session_state["cfg"]["current_iteration"] = 1

st.sidebar.markdown("""---""")
st.session_state["cfg"]["mab_config"]["exploration_share"] = st.sidebar.number_input(
    "Share of exploration rounds, (0.01... 0.99):",
    value=st.session_state["cfg"]["mab_config"]["exploration_share"],
    min_value=0.01,
    max_value=0.99,
)

st.sidebar.write(
    f"""
    MAB trials: \n 
    - total: {mab_trials} \n 
    - explore: {int(mab_trials*st.session_state["cfg"]["mab_config"]["exploration_share"])} \n
    - exploit: {mab_trials-int(mab_trials*st.session_state["cfg"]["mab_config"]["exploration_share"])} \n
    """
)

# START SIMUALTION
st.sidebar.markdown("""---""")
if st.sidebar.button("Start"):

    # init rewards, bandits and data
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

    go_scatters, go_histogtrams, go_bars = {}, {}, {}

    # Streamlit plots
    left_col, mid_col, right_col = st.columns(spec=[0.4, 0.3, 0.3], gap="large")
    st_scatters, st_histogtrams, st_bars = {}, {}, {}

    for algorithm in st.session_state["cfg"]["algorithms"]:
        go_scatters[algorithm] = get_scatters(
            trace_ids=arm_ids,
            x_name=st.session_state["cfg"]["trial_variable"],
            y_name=reward_var_name,
            title=algorithm,
        )
        with left_col:
            st_scatters[algorithm] = st.empty()

        go_histogtrams[algorithm] = get_histograms(
            trace_ids=arm_ids, x_name=reward_var_name, title=algorithm
        )
        with mid_col:
            st_histogtrams[algorithm] = st.empty()

        go_bars[algorithm] = get_bars(
            trace_ids=arm_ids,
            x_name=st.session_state["cfg"]["trial_variable"],
            title=algorithm,
            max_y=mab_trials,
        )
        with right_col:
            st_bars[algorithm] = st.empty()

    # Update the plots with delay
    for iter in range(st.session_state["cfg"]["current_iteration"], mab_trials):

        # Interim results to display
        total_y = {algorithm: 0 for algorithm in st.session_state["cfg"]["algorithms"]}
        total_trials = {algorithm: 0 for algorithm in st.session_state["cfg"]["algorithms"]}

        # Update plotly plots
        for trace, arm_id in enumerate(arm_ids):

            # Scatters
            for alg_name, go_scatter in go_scatters.items():
                y = data[alg_name]["y"][arm_id][: iter + 1]
                y_cum = data[alg_name]["y_cumulative"][arm_id][: iter + 1]
                total_y[alg_name] += y_cum[-1]
                go_scatter.data[trace].x = list(range(0, iter))
                go_scatter.data[trace].y = (
                    y_cum if st.session_state["cfg"]["show_cumulative"] else y
                )

            # Histograms
            for alg_name, go_hist in go_histogtrams.items():
                y_array = np.array(data[alg_name]["y"][arm_id][: iter + 1])
                y_nozero = y_array[y_array != 0]  # Zeros, when arm is not pulled
                if st.session_state["cfg"]["use_boostrap"]:
                    y_nozero = bootstrap(y_nozero, repeats=trials)
                go_hist.data[trace].x = y_nozero

            # Bars
            for alg_name, go_bar in go_bars.items():
                try:
                    y = data[alg_name]["trials_count_cumulative"][arm_id][iter]
                    total_trials[alg_name] += y
                except IndexError:  # Happens because trials of A-B and MAB are imbalanced
                    y = np.array(data[alg_name]["trials_count_cumulative"][arm_id][trials])
                    total_trials[alg_name] = mab_trials
                go_bar.data[trace].x = [arm_id]
                go_bar.data[trace].y = [y]

        # Update Streamlit plots
        for alg_name, st_scatter in st_scatters.items():
            go_scatters[alg_name].update_layout(
                title=f"{alg_name}: achieved {reward_var_name} ({int(total_y[alg_name])})"
            )
            st_scatter.plotly_chart(
                go_scatters[alg_name],
                use_container_width=True,
            )

        for alg_name, st_histogram in st_histogtrams.items():
            st_histogram.plotly_chart(go_histogtrams[alg_name], use_container_width=True)

        for alg_name, st_bar in st_bars.items():
            go_bars[alg_name].update_layout(
                title=f"{alg_name}: total trials ({int(total_trials[alg_name])})"
            )
            st_bar.plotly_chart(go_bars[alg_name], use_container_width=True)

        time.sleep(sleep_time)

    st.session_state["cfg"]["current_iteration"] = 0
