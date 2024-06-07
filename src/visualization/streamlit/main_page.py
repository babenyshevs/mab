import base64
import os

import streamlit as st

from src.general.io import read_yaml

st.set_page_config(page_title="Main page", page_icon="📊", layout="wide")

dir_path = os.path.dirname(os.path.realpath(__file__))
fig_path = dir_path.replace("src/visualization/streamlit", "reports/figures/streamlit")
if "cfg" not in st.session_state:
    st.session_state["cfg"] = read_yaml(f"{dir_path}/default.yml")

st.markdown(
    """
    ---
    # A/B Test and Multi-Armed Bandit for service metrics improvement
    ## Navigation
    Welcome to the MAB vs. A/B Test Visualization App.
    Use the sidebar to navigate to different pages.
    - Simulation: Adjust reward settings for different arms.
    - Data: Compare the performance of A/B Testing and Multi-Armed Bandit.
    - Algorithm: Learn about different algorithms used in A/B Testing and Multi-Armed Bandit.

    ---
    ## Author
        """
)

left_col, mid_col, right_col = st.columns(spec=[0.2, 0.4, 0.4], gap="large")
with left_col:
    st.image("./reports/figures/streamlit/author.jpg", width=200)
with mid_col:
    st.markdown(
        """
        **STANISLAV BABENYSHEV**

        **Senior Data Scientist at DTIT CZ**

        stanislav.babenyshev@external.telekom.de
        """
    )
with right_col:
    st.image("./reports/figures/streamlit/chapter_logo.png", width=500)

file_ = open("./reports/figures/streamlit/fm_screenshots/gif.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()


st.markdown(
    f"--- \n## Frag Magenta Chatbot. \n<img src='data:image/gif;base64,{data_url}' width='1000'>",
    unsafe_allow_html=True,
)
