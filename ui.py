import difflib
import io
import json
import logging
import math
import os
import tempfile
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover - optional dependency
    go = None

try:
    from pyvis.network import Network
except Exception:  # pragma: no cover - optional dependency
    Network = None

from network.network_coordination_detector import build_validation_graph
from validation_integrity_pipeline import analyze_validation_integrity

try:
    from validator_reputation_tracker import update_validator_reputations
except Exception:  # pragma: no cover - optional dependency
    update_validator_reputations = None

from typing import Any, cast

from llm_backends import get_backend
from protocols import AGENT_REGISTRY

try:
    st_secrets = st.secrets
except Exception:  # pragma: no cover - optional in dev/CI
    st_secrets = {
        "SECRET_KEY": "dev",
        "DATABASE_URL": "sqlite:///:memory:",
    }

logger = logging.getLogger(__name__)
logger.propagate = False


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


def diff_results(old: dict | None, new: dict) -> str:
    """Return a unified diff between two result dictionaries."""
    if not old:
        return ""
    old_txt = json.dumps(old, indent=2, sort_keys=True).splitlines()
    new_txt = json.dumps(new, indent=2, sort_keys=True).splitlines()
    diff = difflib.unified_diff(
        old_txt,
        new_txt,
        fromfile="previous",
        tofile="new",
        lineterm="",
    )
    return "\n".join(diff)


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

    class Config:  # type: ignore[no-redef]
        METRICS_PORT = 1234


if VCConfig is None:

    class VCConfig:  # type: ignore[no-redef]
        HIGH_RISK_THRESHOLD = 0.7
        MEDIUM_RISK_THRESHOLD = 0.4


if HarmonyScanner is None:

    class HarmonyScanner:  # type: ignore[no-redef]
        def __init__(self, *_a, **_k):
            pass

        def scan(self, _data):
            return {"dummy": True}


def run_analysis(validations, *, layout: str = "force"):
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

        # Offer GraphML download of the constructed graph
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".graphml")
        try:
            nx.write_graphml(G, tmp_file.name)
            with open(tmp_file.name, "rb") as gm_file:
                data = gm_file.read()
            st.download_button("Download GraphML", data, file_name="graph.graphml")
        except Exception as exc:  # pragma: no cover - optional
            logger.warning(f"GraphML export failed: {exc}")
        finally:
            tmp_file.close()
            try:
                os.remove(tmp_file.name)
            except OSError:
                pass

        # Determine layout
        if layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "grid":
            side = math.ceil(math.sqrt(len(G)))
            pos = {n: (i % side, i // side) for i, n in enumerate(G.nodes())}
        else:
            pos = nx.spring_layout(G, seed=42)

        # Load validator reputations if available
        reputations = {}
        if update_validator_reputations:
            try:
                rep_result = update_validator_reputations(validations)
                reputations = rep_result.get("reputations", {})
            except Exception as exc:  # pragma: no cover - optional
                logger.warning(f"Reputation calc failed: {exc}")

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
            node_sizes = []
            node_colors = []
            max_rep = max(reputations.values()) if reputations else 1.0
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                texts.append(str(node))
                rep = reputations.get(node)
                node_sizes.append(10 + (rep or 0) * 20)
                node_colors.append(rep if rep is not None else 0.5)

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=texts,
                hoverinfo="text",
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    colorscale="Viridis",
                    cmin=0,
                    cmax=max_rep,
                    showscale=bool(reputations),
                ),
            )

            fig = go.Figure(data=[edge_trace, node_trace])
            st.subheader("Validator Coordination Graph")
            st.plotly_chart(fig, use_container_width=True)

            img_buf = io.BytesIO()
            try:
                fig.write_image(img_buf, format="png")
                img_buf.seek(0)
                st.download_button(
                    "Download Graph Image",
                    img_buf.getvalue(),
                    file_name="graph.png",
                )
            except Exception as exc:  # pragma: no cover - optional
                logger.warning(f"Image export failed: {exc}")

            gm_buf = io.BytesIO()
            try:
                nx.write_graphml(G, gm_buf)
                gm_buf.seek(0)
                st.download_button(
                    "Download GraphML",
                    gm_buf.getvalue(),
                    file_name="graph.graphml",
                )
            except Exception as exc:  # pragma: no cover - optional
                logger.warning(f"GraphML export failed: {exc}")
        elif Network is not None:
            net = Network(height="450px", width="100%")
            max_rep = max(reputations.values()) if reputations else 1.0
            for u, v, w in edges:
                for node in (u, v):
                    if node not in net.node_ids:
                        rep = reputations.get(node)
                        size = 15 + (rep or 0) * 20
                        color = "#4da6ff"
                        net.add_node(node, label=node, size=size, color=color)
                net.add_edge(u, v, value=w)
            st.subheader("Validator Coordination Graph")
            net.show("graph.html")
            with open("graph.html") as f:
                html_data = f.read()
            os.remove("graph.html")
            st.components.v1.html(html_data, height=500)
        else:
            weights = [G[u][v]["weight"] * 3 for u, v in G.edges()]
            node_sizes = [300 + (reputations.get(n, 0) * 600) for n in G.nodes()]
            node_colors = [reputations.get(n, 0.5) for n in G.nodes()]
            fig, ax = plt.subplots()
            nx.draw(
                G,
                pos,
                with_labels=True,
                width=weights,
                node_size=node_sizes,
                node_color=node_colors,
                cmap=plt.cm.viridis,
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
    run_analysis([], layout="force")


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
    if "agent_output" not in st.session_state:
        st.session_state["agent_output"] = None
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

    view = st.selectbox("View", ["force", "circular", "grid"], index=0)

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
        st.write(
            f"Session start: {datetime.utcnow().isoformat(timespec='seconds')} UTC"
        )

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
        rerun_clicked = False
        if st.session_state.get("last_result") is not None:
            rerun_clicked = st.button("Re-run This Dataset with New Thresholds")

        st.markdown(f"**Runs this session:** {st.session_state['run_count']}")
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

        st.subheader("Agent Playground")
        agent_names = list(AGENT_REGISTRY.keys())
        agent_choice = st.selectbox("Agent", agent_names)
        backend_choice = st.selectbox(
            "LLM Backend",
            ["dummy", "GPT-4o", "Claude-3", "Gemini"],
            index=0,
        )
        key_map = {
            "GPT-4o": "OPENAI_API_KEY",
            "Claude-3": "ANTHROPIC_API_KEY",
            "Gemini": "GOOGLE_API_KEY",
        }
        api_key = ""
        if backend_choice in key_map:
            api_key = st.text_input(
                f"{backend_choice} API Key",
                value=st_secrets.get(key_map[backend_choice], ""),
                type="password",
            )
        event_type = st.text_input("Event", value="LLM_INCOMING")
        payload_txt = st.text_area("Payload JSON", value="{}", height=100)
        run_agent_clicked = st.button("Run Agent")

    if run_clicked or rerun_clicked:
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
                        "validations": [{"validator": "A", "target": "B", "score": 0.9}]
                    }
                st.session_state["validations_json"] = json.dumps(data, indent=2)
            elif uploaded_file is not None:
                data = json.load(uploaded_file)
                st.session_state["validations_json"] = json.dumps(data, indent=2)
            else:
                st.error("Please upload a file, paste JSON, or enable demo mode.")
                st.stop()
        else:
            try:
                data = json.loads(st.session_state.get("validations_json", ""))
            except Exception as exc:
                st.error(f"Stored validations invalid: {exc}")
                st.stop()
        prev_result = st.session_state.get("last_result")
        result = run_analysis(data.get("validations", []), layout=view)
        diff = diff_results(prev_result, result)
        st.session_state["run_count"] += 1
        st.session_state["last_result"] = result
        st.session_state["last_run"] = datetime.utcnow().isoformat(timespec="seconds")
        st.session_state["analysis_diary"].append(
            {
                "timestamp": st.session_state["last_run"],
                "score": result.get("integrity_analysis", {}).get(
                    "overall_integrity_score"
                ),
                "risk": result.get("integrity_analysis", {}).get("risk_level"),
            }
        )
        st.session_state["diary"].append(
            {
                "timestamp": st.session_state["last_run"],
                "note": f"Run {st.session_state['run_count']} completed",
            }
        )
        if diff:
            st.subheader("Result Diff vs Previous Run")
            st.code(diff)

    if run_agent_clicked:
        try:
            payload = json.loads(payload_txt or "{}")
        except Exception as exc:
            st.error(f"Invalid payload: {exc}")
        else:
            backend_fn = get_backend(backend_choice.lower(), api_key or None)
            agent_cls = AGENT_REGISTRY.get(agent_choice, {}).get("cls")
            if agent_cls is None:
                st.error("Unknown agent selected")
            else:
                try:
                    if agent_choice == "CI_PRProtectorAgent":
                        talker = backend_fn or (lambda p: p)
                        agent = agent_cls(talker, llm_backend=backend_fn)
                    elif agent_choice == "MetaValidatorAgent":
                        agent = agent_cls({}, llm_backend=backend_fn)
                    elif agent_choice == "GuardianInterceptorAgent":
                        agent = agent_cls(llm_backend=backend_fn)
                    else:
                        agent = agent_cls(llm_backend=backend_fn)
                    result = agent.process_event(
                        {"event": event_type, "payload": payload}
                    )
                    st.session_state["agent_output"] = result
                    st.success("Agent executed")
                except Exception as exc:
                    st.session_state["agent_output"] = {"error": str(exc)}
                    st.error(f"Agent error: {exc}")

    if st.session_state.get("agent_output") is not None:
        st.subheader("Agent Output")
        st.json(st.session_state["agent_output"])

    st.subheader("Virtual Diary")
    with st.expander("📘 Notes", expanded=False):
        diary_note = st.text_input("Add note")
        rfc_input = st.text_input("Referenced RFC IDs (comma separated)")
        if st.button("Append Note"):
            entry = {
                "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
                "note": diary_note,
            }
            rfc_ids = [r.strip() for r in rfc_input.split(",") if r.strip()]
            if rfc_ids:
                entry["rfc_ids"] = rfc_ids
            st.session_state["diary"].append(entry)
        for i, entry in enumerate(st.session_state["diary"]):
            anchor = f"diary-{i}"
            note = entry.get("note", "")
            rfc_list = entry.get("rfc_ids")
            extra = f" (RFCs: {', '.join(rfc_list)})" if rfc_list else ""
            st.markdown(
                f"<p id='{anchor}'><strong>{entry['timestamp']}</strong>: {note}{extra}</p>",
                unsafe_allow_html=True,
            )
        if st.download_button(
            "Export Diary as Markdown",
            "\n".join(
                [
                    f"* {e['timestamp']}: {e.get('note', '')}"
                    + (
                        f" (RFCs: {', '.join(e['rfc_ids'])})"
                        if e.get("rfc_ids")
                        else ""
                    )
                    for e in st.session_state["diary"]
                ]
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
        filter_text = st.text_input("Filter RFCs")
        preview_all = st.checkbox("Preview full text")

        def parse_summary(text: str) -> str:
            if "## Summary" not in text:
                return ""
            part = text.split("## Summary", 1)[1]
            lines = []
            for line in part.splitlines()[1:]:
                if line.startswith("##"):
                    break
                if line.strip():
                    lines.append(line.strip())
            return " ".join(lines)

        rfc_paths = sorted(rfc_dir.rglob("rfc-*.md"))
        rfc_entries: list[dict[str, Any]] = []
        for path in rfc_paths:
            text = path.read_text()
            summary = parse_summary(text)
            rfc_entries.append(
                {"id": path.stem, "summary": summary, "text": text, "path": path}
            )

        diary_mentions: dict[str, list[int]] = {e["id"]: [] for e in rfc_entries}  # type: ignore[misc]
        for i, entry in enumerate(st.session_state.get("diary", [])):
            note_lower = entry.get("note", "").lower()
            ids = set(e.strip().lower() for e in entry.get("rfc_ids", []) if e)
            for rfc in rfc_entries:
                rid = str(rfc["id"]).lower()
                if (
                    rid in note_lower
                    or rid.replace("-", " ") in note_lower
                    or rid in ids
                ):
                    diary_mentions.setdefault(rfc["id"], []).append(i)

        for rfc in rfc_entries:
            if (
                filter_text
                and filter_text.lower() not in rfc["summary"].lower()
                and filter_text.lower() not in rfc["id"].lower()
            ):
                continue
            st.markdown(f"### {rfc['id']}")
            st.write(summarize_text(str(rfc["summary"])))
            mentions = diary_mentions.get(rfc["id"], [])
            if mentions:
                links = ", ".join(
                    [f"[entry {idx + 1}](#diary-{idx})" for idx in mentions]
                )
                st.markdown(f"Referenced in: {links}", unsafe_allow_html=True)
            st.markdown(f"[Read RFC]({cast(Path, rfc['path']).as_posix()})")
            if preview_all or st.checkbox("Show details", key=f"show_{rfc['id']}"):
                st.markdown(rfc["text"], unsafe_allow_html=True)

    st.subheader("Protocols")
    with st.expander("Repository Protocols", expanded=False):
        proto_dir = Path("protocols")
        files = sorted([p for p in proto_dir.glob("*.py") if p.is_file()])
        for file in files:
            st.markdown(f"- [{file.name}]({file.as_posix()})")

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
