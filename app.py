import json
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

from validation_integrity_pipeline import analyze_validation_integrity
from network.network_coordination_detector import build_validation_graph

st.set_page_config(page_title="superNova_2177 Demo")
st.title("superNova_2177 Validation Analyzer")

st.markdown(
    "Upload a JSON file with a `validations` array or run the demo to see the pipeline in action."
)


def run_analysis(validations):
    if not validations:
        st.error("No validations found in the uploaded file.")
        return

    with st.spinner("Running analysis..."):
        result = analyze_validation_integrity(validations)
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
        nx.draw(G, pos, with_labels=True, width=weights, node_color="#4da6ff", ax=ax)
        st.subheader("Validator Coordination Graph")
        st.pyplot(fig)


if st.button("Run Demo"):
    with open("sample_validations.json") as f:
        data = json.load(f)
    run_analysis(data.get("validations", []))

uploaded_file = st.file_uploader("Upload validations JSON", type="json")
if uploaded_file is not None:
    data = json.load(uploaded_file)
    run_analysis(data.get("validations", []))

