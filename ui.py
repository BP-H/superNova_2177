import json
import logging
from pathlib import Path

import os
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
from datetime import datetime

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover - optional dependency
    go = None

try:
    from pyvis.network import Network
except Exception:  # pragma: no cover - optional dependency
    Network = None

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


def summarize_text(text: str, max_len: int = 150) -> str:
    """Basic text summarizer placeholder."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def clear_memory(state: dict) -> None:
    """Reset analysis tracking state."""
    state["analysis_diary"] = []
    state["run_count"] = 0
    state["last_result"] = None
    state["last_run"] = None


def export_latest_result(state: dict) -> str:
    """Return the latest result as a JSON blob."""
    return json.dumps(state.get("last_result", {}), indent=2)


def generate_explanation(result: dict) -> str:
    """Generate a human readable integrity summary."""
    integrity = result.get("integrity_analysis", {})
    if not integrity:
        return "No integrity analysis available."
    risk = integrity.get("risk_level", "unknown")
    score = integrity.get("overall_integrity_score", "N/A")
    lines = [f"Risk level: {risk}", f"Integrity score: {score}"]
    recs = result.get("recommendations") or []
    if recs:
        lines.append("Recommendations:")
        for r in recs:
            lines.append(f"- {r}")
    return "\n".join(lines)

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

        if go is not None:
            edge_x = []
            edge_y = []
            for u, v in G.edges():
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]
            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=0.5, color="#888"),
                hoverinfo="none",
                mode="lines",
            )

            node_x = []
            node_y = []
            texts = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                texts.append(str(node))

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=texts,
                hoverinfo="text",
                marker=dict(size=10, color="#4da6ff"),
            )

            fig = go.Figure(data=[edge_trace, node_trace])
            st.subheader("Validator Coordination Graph")
            st.plotly_chart(fig, use_container_width=True)
        elif Network is not None:
            net = Network(height="450px", width="100%")
            for u, v, w in edges:
                net.add_node(u, label=u)
                net.add_node(v, label=v)
                net.add_edge(u, v, value=w)
            st.subheader("Validator Coordination Graph")
            net.show("graph.html")
            with open("graph.html") as f:
                st.components.v1.html(f.read(), height=500)
        else:
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

    if st.button("Explain This Score"):
        explanation = generate_explanation(result)
        with st.expander("Score Explanation"):
            st.markdown(explanation)

    return result


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

    if "diary" not in st.session_state:
        st.session_state["diary"] = []
    if "analysis_diary" not in st.session_state:
        st.session_state["analysis_diary"] = []
    if "run_count" not in st.session_state:
        st.session_state["run_count"] = 0
    if "last_result" not in st.session_state:
        st.session_state["last_result"] = None
    if "last_run" not in st.session_state:
        st.session_state["last_run"] = None
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    if st.session_state["theme"] == "dark":
        st.markdown(
            """
            <style>
            body, .stApp { background-color: #1e1e1e; color: #f0f0f0; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    st.title("superNova_2177 Validation Analyzer")
    st.markdown(
        "Upload a JSON file with a `validations` array, paste JSON below, "
        "or enable demo mode to see the pipeline in action."
    )
    disclaimer = (
        "\u26a0\ufe0f Metrics like Harmony Score and Resonance are purely symbolic "
        "and carry no monetary value. See README.md lines 12–13 for the full "
        "disclaimer."
    )
    st.markdown(
        f"<span title='{disclaimer}'><em>{disclaimer}</em></span>",
        unsafe_allow_html=True,
    )

    if "validations_json" not in st.session_state:
        st.session_state["validations_json"] = ""

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
        st.write(f"ENV: {os.getenv('ENV', 'dev')}")
        st.write(f"Session start: {datetime.utcnow().isoformat(timespec='seconds')} UTC")

        if secret_key:
            st.success("Secret key loaded")
        else:
            st.warning("SECRET_KEY missing")

        st.divider()
        st.subheader("Settings")
        demo_mode = st.checkbox("Demo mode")
        st.session_state["theme"] = "dark" if st.checkbox("Dark theme") else "light"
        VCConfig.HIGH_RISK_THRESHOLD = st.slider(
            "High Risk Threshold", 0.1, 1.0, float(VCConfig.HIGH_RISK_THRESHOLD), 0.05
        )

        uploaded_file = st.file_uploader(
            "Upload validations JSON (drag/drop)", type="json"
        )
        run_clicked = st.button("Run Analysis")

        st.markdown(
            f"**Runs this session:** {st.session_state['run_count']}"
        )
        if st.session_state.get("last_run"):
            st.write(f"Last run: {st.session_state['last_run']}")
        if st.button("Clear Memory"):
            clear_memory(st.session_state)
            st.session_state["diary"] = []
        export_blob = export_latest_result(st.session_state)
        st.download_button(
            "Export Latest Result",
            export_blob,
            file_name="latest_result.json",
        )
        st.divider()

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
        result = run_analysis(data.get("validations", []))
        st.session_state["run_count"] += 1
        st.session_state["last_result"] = result
        st.session_state["last_run"] = datetime.utcnow().isoformat(timespec="seconds")
        st.session_state["analysis_diary"].append(
            {
                "timestamp": st.session_state["last_run"],
                "score": result.get("integrity_analysis", {}).get("overall_integrity_score"),
                "risk": result.get("integrity_analysis", {}).get("risk_level"),
            }
        )
        st.session_state["diary"].append(
            {
                "timestamp": st.session_state["last_run"],
                "note": f"Run {st.session_state['run_count']} completed",
            }
        )

    st.subheader("Virtual Diary")
    with st.expander("📘 Notes", expanded=False):
        diary_note = st.text_input("Add note")
        if st.button("Append Note"):
            st.session_state["diary"].append(
                {
                    "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
                    "note": diary_note,
                }
            )
        for entry in st.session_state["diary"]:
            st.write(f"{entry['timestamp']}: {entry['note']}")
        if st.download_button(
            "Export Diary as Markdown",
            "\n".join(
                [f"* {e['timestamp']}: {e['note']}" for e in st.session_state["diary"]]
            ),
            file_name="diary.md",
        ):
            pass
        st.download_button(
            "Export Diary as JSON",
            json.dumps(st.session_state["diary"], indent=2),
            file_name="diary.json",
        )

    st.subheader("RFCs and Agent Insights")
    with st.expander("Proposed RFCs", expanded=False):
        rfc_dir = Path("rfcs")
        for path in sorted(rfc_dir.glob("rfc-*.md")):
            text = path.read_text()
            summary = ""
            if "## Summary" in text:
                part = text.split("## Summary", 1)[1]
                summary_lines = []
                for line in part.splitlines()[1:]:
                    if line.startswith("##"):
                        break
                    if line.strip():
                        summary_lines.append(line.strip())
                summary = " ".join(summary_lines)
            st.markdown(f"### {path.stem}")
            st.write(summarize_text(summary))
            st.markdown(f"[Read RFC]({path.as_posix()})")

    notes_path = Path("AgentNotes.md")
    if notes_path.exists():
        notes_content = notes_path.read_text()
    else:
        notes_content = "No notes found."

    with st.expander("Agent’s Internal Thoughts"):
        st.markdown(notes_content)


if __name__ == "__main__":
    logger.info("\u2705 Streamlit UI started. Launching main()...")
    main()
