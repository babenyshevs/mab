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

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    with st.expander("see data", expanded=False):
        st.write(df)

    columns = list(df.columns)
    selected_cols = st.multiselect("variables", options=columns)

    if selected_cols:
        analyzer = SampleSizeGrid(variables=selected_cols, data=df)
        distributions = analyzer.plot_distributions(return_fig=True)
        st.plotly_chart(distributions, use_container_width=True, theme="streamlit")
        obs_needed = analyzer.plot_observation_requirements(return_fig=True)
        st.plotly_chart(obs_needed, use_container_width=True, theme="streamlit")
