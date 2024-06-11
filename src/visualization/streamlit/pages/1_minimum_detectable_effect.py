import os
from typing import List

import pandas as pd
import streamlit as st

from src.general.io import read_yaml
from src.visualization.sample_size_grid import SampleSizeGrid

st.set_page_config(page_title="Data", page_icon="📊", layout="wide")

# Initialize configuration if not already in session state
if "cfg" not in st.session_state:
    dir_path = os.path.dirname(os.path.realpath(__file__)).replace("pages", "")
    st.session_state["cfg"] = read_yaml(f"{dir_path}default.yml")


file = st.file_uploader("Choose a CSV file", type="csv")
if file is not None:
    st.session_state["data_mde"] = pd.read_csv(file)

if "data_mde" in st.session_state.keys():
    with st.expander("see data", expanded=False):
        st.write(st.session_state["data_mde"])

    columns = list(st.session_state["data_mde"].columns)
    selected_cols = st.multiselect("variables", options=columns)

    if selected_cols:
        analyzer = SampleSizeGrid(variables=selected_cols, data=st.session_state["data_mde"])
        obs_needed = analyzer.plot_observation_requirements(return_fig=True)
        st.plotly_chart(obs_needed, use_container_width=True, theme="streamlit")
        distributions = analyzer.plot_distributions(return_fig=True)
        st.plotly_chart(distributions, use_container_width=True, theme="streamlit")

    with st.expander("source", expanded=False):
        st.markdown(
            """
            For power analysis **statmodels** are used:
            statsmodels.stats.power.TTestIndPower
            """
        )
