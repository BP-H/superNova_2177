# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

import os
import streamlit as st

st.set_page_config(page_title="superNova_2177", layout="centered")

HEALTH_CHECK_PARAM = "healthz"

if st.query_params.get(HEALTH_CHECK_PARAM) == "1" or os.environ.get("PATH_INFO", "").rstrip("/") == "/healthz":
    st.write("ok")
    st.stop()

st.title("superNova_2177")
st.write(
    "Welcome to the superNova_2177 project. This lightweight Streamlit page confirms that the application is running."
)
st.markdown(
    "[Launch the full NiceGUI interface](https://github.com/BP-H/superNova_2177)",
    unsafe_allow_html=True,
)
