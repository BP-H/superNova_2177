import json

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from network.network_coordination_detector import build_validation_graph
from validation_integrity_pipeline import analyze_validation_integrity

try:
    from config import Config
    from superNova_2177 import HarmonyScanner
except Exception:  # pragma: no cover - optional debug dependencies
    HarmonyScanner = None  # type: ignore
    Config = None  # type: ignore


def run_analysis(validations):
    """Execute the validation integrity pipeline and display results."""
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


def boot_diagnostic_ui():
    """Render a simple diagnostics UI used during boot."""
    st.set_page_config(page_title="Boot Diagnostic", layout="centered")
    st.header("Boot Diagnostic")

    st.subheader("Config Test")
    if Config is not None:
        st.success("Config import succeeded")
        st.write({"METRICS_PORT": Config.METRICS_PORT})
    else:
        st.error("Config import failed")

    st.subheader("Harmony Scanner Check")
    scanner = HarmonyScanner(Config()) if Config and HarmonyScanner else None
    if scanner:
        st.success("HarmonyScanner instantiated")
    else:
        st.error("HarmonyScanner init failed")

    if st.button("Run Dummy Scan") and scanner:
        try:
            scanner.scan("hello world")
            st.success("Dummy scan completed")
        except Exception as exc:  # pragma: no cover - debug only
            st.error(f"Dummy scan error: {exc}")


def main() -> None:
    """Main entry point for the validation analysis UI."""
    st.set_page_config(page_title="superNova_2177 Demo")
    st.title("superNova_2177 Validation Analyzer")
    st.markdown(
        "Upload a JSON file with a `validations` array or enable demo "
        "mode to see the pipeline in action."
    )

    secret_key = st.secrets.get("SECRET_KEY", "not set")
    database_url = st.secrets.get("DATABASE_URL", "not set")

    with st.sidebar:
        st.header("Environment")
        st.write(f"Database URL: {database_url}")
        if secret_key != "not set":
            st.success("Secret key loaded")
        else:
            st.warning("SECRET_KEY missing")
        demo_mode = st.checkbox("Demo mode")
        uploaded_file = st.file_uploader("Upload validations JSON", type="json")
        run_clicked = st.button("Run Analysis")

    if run_clicked:
        if demo_mode:
            try:
                with open("sample_validations.json") as f:
                    data = json.load(f)
            except FileNotFoundError:
                st.warning(
                    "sample_validations.json not found, loading fallback demo data"
                )
                data = {
                    "validations": [
                        {
                            "validator_id": "demo_user",
                            "score": 0.9,
                            "confidence": 0.8,
                            "signal_strength": 0.75,
                            "note": "Example validation",
                            "timestamp": "2025-01-01T00:00:00Z",
                            "specialty": "example",
                            "affiliation": "DemoOrg",
                        },
                        {
                            "validator_id": "demo_partner",
                            "score": 0.85,
                            "confidence": 0.7,
                            "signal_strength": 0.65,
                            "note": "Another validation",
                            "timestamp": "2025-01-02T00:00:00Z",
                            "specialty": "example",
                            "affiliation": "DemoOrg",
                        },
                    ]
                }
        elif uploaded_file is not None:
            data = json.load(uploaded_file)
        else:
            st.error("Please upload a file or enable demo mode.")
            st.stop()
        run_analysis(data.get("validations", []))


if __name__ == "__main__":
    main()
