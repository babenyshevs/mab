import os

import streamlit as st

from src.general.io import read_yaml

st.set_page_config(layout="wide")

if "cfg" not in st.session_state:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    st.session_state["cfg"] = read_yaml(f"{dir_path}/default.yml")


st.title("Comparison of A/B test and MAB on data")
st.header("Hello Page")
st.write("Welcome to the MAB vs. A/B Test Visualization App.")
st.write("Use the sidebar to navigate to different pages.")
st.write("- Configuration: Adjust reward settings for different arms.")
st.write("- Visualization: Compare the performance of A/B Testing and Multi-Armed Bandit.")
