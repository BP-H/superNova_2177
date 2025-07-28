import json
import logging

import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import streamlit as st

logger = logging.getLogger(__name__)
logger.propagate = False

try:
    st_secrets = st.secrets
except Exception:  # pragma: no cover - optional in dev/CI
    st_secrets = {
        "SECRET_KEY": "dev",
        "DATABASE_URL": "sqlite:///:memory:",
    }

from network.network_coordination_detector import build_validation_graph
from validation_integrity_pipeline import analyze_validation_integrity

try:
    from validation_certifier import Config as VCConfig
except Exception:  # pragma: no cover - optional debug dependencies
    VCConfig = None  # type: ignore

try:
    from config import Config
    from superNova_2177 import HarmonyScanner
except Exception:  # pragma: no cover - optional debug dependencies
    HarmonyScanner = None  # type: ignore
    Config = None  # type: ignore

if Config is None:
    class Config:
        METRICS_PORT = 1234

if VCConfig is None:
    class VCConfig:
        HIGH_RISK_THRESHOLD = 0.7
        MEDIUM_RISK_THRESHOLD = 0.4

if HarmonyScanner is None:
    class HarmonyScanner:
        def __init__(self, *_a, **_k):
            pass

        def scan(self, _data):
            return {"dummy": True}


def clear_memory() -> None:
    """Reset analysis history and run counters."""
    st.session_state["analysis_diary"] = []
    st.session_state["run_count"] = 0
    st.session_state["last_run"] = None
    st.session_state["last_result"] = None
    st.session_state["show_explanation"] = False


def export_latest_result() -> str | None:
    """Return the most recent analysis result as a JSON string."""
    result = st.session_state.get("last_result")
    if not result:
        return None
    return json.dumps(result, indent=2)


def generate_explanation(result: dict) -> str:
    """Return a human-readable explanation for the integrity score."""
    integrity = result.get("integrity_analysis", {})
    score = integrity.get("overall_integrity_score")
    risk = integrity.get("risk_level")
    recs = result.get("recommendations", [])
    if score is None:
        return "No integrity information available."
    text = (
        f"The overall integrity score is {score:.2f}, indicating {risk} risk level."
    )
    if recs:
        text += " Recommended actions: " + "; ".join(recs)
    return text


def run_analysis(validations):
    """Execute the validation integrity pipeline and display results."""
    if not validations:
        try:
            with open("sample_validations.json") as f:
                sample = json.load(f)
                validations = sample.get("validations", [])
        except Exception:
            validations = [{"validator": "A", "target": "B", "score": 0.5}]
        st.warning("No validations provided – using fallback data.")
        print("✅ UI diagnostic agent active")

    with st.spinner("Running analysis..."):
        result = analyze_validation_integrity(validations)

    st.session_state.setdefault("run_count", 0)
    st.session_state.setdefault("analysis_diary", [])
    st.session_state["run_count"] += 1
    st.session_state["last_run"] = datetime.utcnow().isoformat()
    st.session_state["last_result"] = result
    st.session_state["analysis_diary"].append(result)

    consensus = result.get("consensus_score")
    if consensus is not None:
        st.metric("Consensus Score", round(consensus, 3))

    integrity = result.get("integrity_analysis", {})
    score = integrity.get("overall_integrity_score")
    if score is not None:
        color = "green"
        if score < VCConfig.MEDIUM_RISK_THRESHOLD:
            color = "red"
        elif score < VCConfig.HIGH_RISK_THRESHOLD:
            color = "yellow"
        tooltip = (
            f"Green \u2265 {VCConfig.HIGH_RISK_THRESHOLD}, "
            f"Yellow \u2265 {VCConfig.MEDIUM_RISK_THRESHOLD}, "
            f"Red < {VCConfig.MEDIUM_RISK_THRESHOLD}"
        )
        st.markdown(
            f"<span title='{tooltip}' "
            f"style='background-color:{color};color:white;"
            f"padding:0.25em 0.5em;border-radius:0.25em;'>"
            f"Integrity Score: {score:.2f}</span>",
            unsafe_allow_html=True,
        )

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

    st.subheader("Validation Analysis")
    run_analysis([])


def main() -> None:
    """Main entry point for the validation analysis UI."""
    st.set_page_config(page_title="superNova_2177 Demo")
    st.title("superNova_2177 Validation Analyzer")
    st.markdown(
        "Upload a JSON file with a `validations` array, paste JSON below, "
        "or enable demo mode to see the pipeline in action."
    )

    defaults = {
        "validations_json": "",
        "analysis_diary": [],
        "run_count": 0,
        "last_run": None,
        "last_result": None,
        "show_explanation": False,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    validations_input = st.text_area(
        "Validations JSON",
        value=st.session_state["validations_json"],
        height=200,
        key="validations_editor",
    )
    if st.button("Reset to Demo"):
        try:
            with open("sample_validations.json") as f:
                demo_data = json.load(f)
            st.session_state["validations_json"] = json.dumps(demo_data, indent=2)
        except FileNotFoundError:
            st.warning("Demo file not found")
        st.experimental_rerun()

    secret_key = st_secrets.get("SECRET_KEY")
    database_url = st_secrets.get("DATABASE_URL")

    with st.sidebar:
        st.header("Environment")
        st.write(f"Database URL: {database_url or 'not set'}")
        if secret_key:
            st.success("Secret key loaded")
        else:
            st.warning("SECRET_KEY missing")
        demo_mode = st.checkbox("Demo mode")
        uploaded_file = st.file_uploader("Upload validations JSON", type="json")
        run_clicked = st.button("Run Analysis")

        st.divider()
        st.subheader("Dashboard")
        st.write(f"Run count: {st.session_state['run_count']}")
        st.write(f"Last run: {st.session_state.get('last_run', 'Never')}")

        if st.button("Clear Memory"):
            clear_memory()
            st.experimental_rerun()

        if st.session_state.get("last_result"):
            st.download_button(
                "Export Report",
                export_latest_result(),
                file_name="analysis_report.json",
                mime="application/json",
            )
        if st.button("Explain This Score", key="explain_btn"):
            st.session_state["show_explanation"] = True

    if run_clicked:
        if validations_input.strip():
            try:
                data = json.loads(validations_input)
                st.session_state["validations_json"] = json.dumps(data, indent=2)
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")
                st.stop()
        elif demo_mode:
            try:
                with open("sample_validations.json") as f:
                    data = json.load(f)
            except FileNotFoundError:
                st.warning("Demo file not found, using default dataset.")
                data = {
                    "validations": [
                        {"validator": "A", "target": "B", "score": 0.9}
                    ]
                }
            st.session_state["validations_json"] = json.dumps(data, indent=2)
        elif uploaded_file is not None:
            data = json.load(uploaded_file)
            st.session_state["validations_json"] = json.dumps(data, indent=2)
        else:
            st.error("Please upload a file, paste JSON, or enable demo mode.")
            st.stop()
        run_analysis(data.get("validations", []))
        if st.session_state.get("show_explanation"):
            with st.expander("Score Explanation", expanded=True):
                st.write(generate_explanation(st.session_state["last_result"]))


if __name__ == "__main__":
    logger.info("\u2705 Streamlit UI started. Launching main()...")
    main()
