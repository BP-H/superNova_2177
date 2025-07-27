"""Streamlit front-end for hypothesis validation analysis."""

import json
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

from validation_integrity_pipeline import analyze_validation_integrity
from network.network_coordination_detector import build_validation_graph


st.set_page_config(page_title="superNova_2177 Demo")
st.title("superNova_2177 Validation Analyzer")

st.markdown(
    "Upload a JSON file with a `validations` array or enable demo "
    "mode to see the pipeline in action."
)

# Load secrets provided by Streamlit Cloud or local .streamlit/secrets.toml
SECRET_KEY = st.secrets.get("SECRET_KEY", "not set")
DATABASE_URL = st.secrets.get("DATABASE_URL", "not set")

st.sidebar.header("Environment")
st.sidebar.write(f"Database URL: {DATABASE_URL}")
if SECRET_KEY != "not set":
    st.sidebar.success("Secret key loaded")
else:
    st.sidebar.warning("SECRET_KEY missing")


def run_analysis(validations):
    if not validations:
        st.error("No validations found in the uploaded file.")
        return

    with st.spinner("Running analysis..."):
        result = analyze_validation_integrity(validations)

    integrity = result.get("integrity_analysis", {})
    score = integrity.get("overall_integrity_score")

    if score is not None:
        st.metric("Integrity Score", score)

    st.subheader("Analysis Result")
    st.json(result)

    graph_data = build_validation_graph(validations)
    edges = graph_data.get("edges", [])
    if edges:
        G = nx.Graph()
        for v1, v2, w in edges:
            G.add_edge(v1, v2, weight=w)
        pos = nx.spring_layout(G, seed=42)
        weights = [G[u][v]["weight"] * 3 for u, v in G.edges()]
        fig, ax = plt.subplots()
        nx.draw(
            G,
            pos,
            with_labels=True,
            width=weights,
            node_color="#4da6ff",
            ax=ax,
        )
        st.subheader("Validator Coordination Graph")
        st.pyplot(fig)


demo_mode = st.checkbox("Demo mode")
uploaded_file = st.file_uploader("Upload validations JSON", type="json")

if st.button("Run Analysis"):
    if demo_mode:
        with open("sample_validations.json") as f:
            data = json.load(f)
    elif uploaded_file is not None:
        data = json.load(uploaded_file)
    else:
        st.error("Please upload a file or enable demo mode.")
        st.stop()

    run_analysis(data.get("validations", []))
