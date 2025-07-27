import json
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

from validation_integrity_pipeline import analyze_validation_integrity
from validate_hypothesis import generate_demo_validations
from network.network_coordination_detector import build_validation_graph


def load_validations(file):
    data = json.load(file)
    if isinstance(data, list):
        return data
    return data.get("validations", [])


def run_analysis(validations):
    result = analyze_validation_integrity(validations)
    graph_info = build_validation_graph(validations)
    edges = graph_info.get("edges", [])
    nodes = list(graph_info.get("nodes", []))

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)

    fig, ax = plt.subplots()
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx(G, pos, ax=ax, with_labels=True, node_color="#7fa9d6")
    ax.set_axis_off()
    return result, fig


def main():
    st.title("superNova_2177 Validation Demo")
    st.write("Upload a JSON validation file or run with demo data.")

    option = st.radio("Input Source", ["Demo Data", "Upload JSON"])
    uploaded_file = None
    if option == "Upload JSON":
        uploaded_file = st.file_uploader("Select validation JSON", type="json")

    if st.button("Run Analysis"):
        if option == "Demo Data":
            validations = generate_demo_validations()
        else:
            if uploaded_file is None:
                st.error("Please upload a JSON file.")
                return
            try:
                validations = load_validations(uploaded_file)
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
                return

        with st.spinner("Running analysis..."):
            result, fig = run_analysis(validations)

        st.subheader("Analysis Result")
        st.json(result)

        st.subheader("Validation Graph")
        st.pyplot(fig)


if __name__ == "__main__":
    main()
