import difflib
import io
import json
import logging
import math
import os
import asyncio
import sys
import traceback
from datetime import datetime
from pathlib import Path
import sys

logger = logging.getLogger(__name__)
logger.propagate = False

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# Basic page setup so Streamlit responds immediately on load
try:
    st.set_page_config(page_title="superNova_2177", layout="wide")
except Exception:
    logger.exception("Failed to configure Streamlit page")
    print("Failed to configure Streamlit page", file=sys.stderr)

else:
    st.title("superNova_2177")
    st.success("\u2705 Streamlit loaded!")
from streamlit_helpers import (
    alert,
    header,
    theme_selector,
    centered_container,
    apply_theme,
)

try:
    from streamlit_app import _run_async
except Exception:

    def _run_async(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        else:
            if loop.is_running():
                return asyncio.run_coroutine_threadsafe(coro, loop).result()
            return loop.run_until_complete(coro)


try:
    from frontend_bridge import dispatch_route
except Exception:  # pragma: no cover - optional dependency
    dispatch_route = None

try:
    from db_models import SessionLocal, Harmonizer, UniverseBranch
except Exception:  # pragma: no cover - missing ORM
    SessionLocal = None  # type: ignore
    Harmonizer = None  # type: ignore
    UniverseBranch = None  # type: ignore

try:
    from introspection.introspection_pipeline import run_full_audit
except Exception:  # pragma: no cover - optional module
    run_full_audit = None  # type: ignore

try:
    from superNova_2177 import cosmic_nexus, agent, InMemoryStorage
except Exception:  # pragma: no cover - optional runtime globals
    cosmic_nexus = None  # type: ignore
    agent = None  # type: ignore
    InMemoryStorage = None  # type: ignore

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

from social_tabs import render_social_tab
from voting_ui import render_voting_tab
from agent_ui import render_agent_insights_tab
try:
    st_secrets = st.secrets
except Exception:  # pragma: no cover - optional in dev/CI
    st_secrets = {
        "SECRET_KEY": "dev",
        "DATABASE_URL": "sqlite:///:memory:",
    }

sample_path = Path(__file__).resolve().parent / "sample_validations.json"

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




def render_pyvis_to_html(net: Any) -> str:
    """Return the interactive HTML for a PyVis network."""
    try:
        return net.generate_html(notebook=False)
    except AttributeError:  # pragma: no cover - fallback for old pyvis
        return net.generate_html()


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


def run_analysis(validations, *, layout: str = "force"):
    """Execute the validation integrity pipeline and display results."""
    if not validations:
        try:
            with open(sample_path) as f:
                sample = json.load(f)
                validations = sample.get("validations", [])
        except Exception:
            validations = [{"validator": "A", "target": "B", "score": 0.5}]
        alert("No validations provided – using fallback data.", "warning")
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

        # Collect voter metadata from the validations
        voter_meta: dict[str, dict[str, str]] = {}
        for entry in validations:
            vid = entry.get("validator_id")
            if not vid:
                continue
            meta = voter_meta.setdefault(vid, {})
            cls = (
                entry.get("validator_class")
                or entry.get("class")
                or entry.get("affiliation")
                or entry.get("specialty")
            )
            species = entry.get("species") or entry.get("validator_species")
            if cls and "voter_class" not in meta:
                meta["voter_class"] = str(cls)
            if species and "species" not in meta:
                meta["species"] = str(species)

        # Add nodes with metadata and default fallbacks
        for node in graph_data.get("nodes", []):
            meta = voter_meta.get(node, {})
            G.add_node(
                node,
                voter_class=meta.get("voter_class", "unknown"),
                species=meta.get("species", "unknown"),
            )

        for v1, v2, w in edges:
            G.add_edge(v1, v2, weight=w)

        # Offer GraphML download of the constructed graph including metadata
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
                if isinstance(rep_result, dict):
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
            html_data = render_pyvis_to_html(net)
            st.components.v1.html(html_data, height=500)
            st.download_button(
                "Download Interactive HTML",
                html_data,
                file_name="graph.html",
            )
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
    header("Boot Diagnostic", layout="centered")

    st.subheader("Config Test")
    if Config is not None:
        st.success("Config import succeeded")
        st.write({"METRICS_PORT": Config.METRICS_PORT})
    else:
        alert("Config import failed", "error")

    st.subheader("Harmony Scanner Check")
    scanner = HarmonyScanner(Config()) if Config and HarmonyScanner else None
    if scanner:
        st.success("HarmonyScanner instantiated")
    else:
        alert("HarmonyScanner init failed", "error")

    if st.button("Run Dummy Scan") and scanner:
        try:
            scanner.scan("hello world")
            st.success("Dummy scan completed")
        except Exception as exc:  # pragma: no cover - debug only
            alert(f"Dummy scan error: {exc}", "error")

    st.subheader("Validation Analysis")
    run_analysis([], layout="force")

def render_validation_ui() -> None:
    """Main entry point for the validation analysis UI."""
    header("superNova_2177 Validation Analyzer", layout="wide")
    st.title("Welcome to superNova_2177")
    st.success("✅ Streamlit loaded!")


    ts_placeholder = st.empty()
    if "session_start_ts" not in st.session_state:
        st.session_state["session_start_ts"] = datetime.utcnow().isoformat(
            timespec="seconds"
        )
    ts_placeholder.markdown(
        f"<div style='position:fixed;top:0;right:0;background:rgba(0,0,0,0.6);color:white;padding:0.25em 0.5em;border-radius:0 0 0 4px;'>Session start: {st.session_state['session_start_ts']} UTC</div>",
        unsafe_allow_html=True,
    )
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
    apply_theme(st.session_state["theme"])
    centered_container()

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
            with open(sample_path) as f:
                demo_data = json.load(f)
            st.session_state["validations_json"] = json.dumps(demo_data, indent=2)
        except FileNotFoundError:
            alert("Demo file not found", "warning")
        st.experimental_rerun()

    secret_key = st_secrets.get("SECRET_KEY")
    database_url = st_secrets.get("DATABASE_URL")

    with st.sidebar:
        st.header("Environment")
        st.write(f"Database URL: {database_url or 'not set'}")
        st.write(f"ENV: {os.getenv('ENV', 'dev')}")
        st.write(f"Session start: {st.session_state['session_start_ts']} UTC")

        if secret_key:
            st.success("Secret key loaded")
        else:
            alert("SECRET_KEY missing", "warning")

        st.divider()
        st.subheader("Settings")
        demo_mode_choice = st.radio("Mode", ["Normal", "Demo"], horizontal=True)
        demo_mode = demo_mode_choice == "Demo"
        theme_selector("Theme")

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
        agent_desc = AGENT_REGISTRY.get(agent_choice, {}).get("description")
        if agent_desc:
            st.caption(agent_desc)
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

        st.divider()
        governance_view = st.checkbox(
            "Governance View", value=st.session_state.get("governance_view", False)
        )
        st.session_state["governance_view"] = governance_view

        show_dev = st.checkbox("Dev Tools")
        if show_dev:
            dev_tabs = st.tabs(
                [
                    "Fork Universe",
                    "Universe State Viewer",
                    "Run Introspection Audit",
                    "Agent Logs",
                    "Inject Event",
                    "Session Inspector",
                    "Playground",
                ]
            )

            with dev_tabs[0]:
                if cosmic_nexus and SessionLocal and Harmonizer:
                    with SessionLocal() as db:
                        user = db.query(Harmonizer).first()
                        if user and st.button("Fork with Mock Config"):
                            try:
                                fork_id = cosmic_nexus.fork_universe(
                                    user, {"entropy_threshold": 0.5}
                                )
                                st.success(f"Forked universe {fork_id}")
                            except Exception as exc:
                                st.error(f"Fork failed: {exc}")
                        elif not user:
                            st.info("No users available to fork")
                else:
                    st.info("Fork operation unavailable")

            with dev_tabs[1]:
                if SessionLocal and UniverseBranch:
                    with SessionLocal() as db:
                        records = (
                            db.query(UniverseBranch)
                            .order_by(UniverseBranch.timestamp.desc())
                            .limit(5)
                            .all()
                        )
                        if records:
                            for r in records:
                                st.write(
                                    {
                                        "id": r.id,
                                        "status": r.status,
                                        "timestamp": r.timestamp,
                                    }
                                )
                        else:
                            st.write("No forks recorded")
                else:
                    st.info("Database unavailable")

            with dev_tabs[2]:
                hid = st.text_input("Hypothesis ID", key="audit_id")
                if st.button("Run Audit") and hid:
                    if dispatch_route and SessionLocal:
                        with SessionLocal() as db:
                            try:
                                result = _run_async(
                                    dispatch_route(
                                        "trigger_full_audit",
                                        {"hypothesis_id": hid},
                                        db=db,
                                    )
                                )
                                st.json(result)
                            except Exception as exc:
                                st.error(f"Audit failed: {exc}")
                    elif run_full_audit and SessionLocal:
                        with SessionLocal() as db:
                            try:
                                result = run_full_audit(hid, db)
                                st.json(result)
                            except Exception as exc:
                                st.error(f"Audit failed: {exc}")
                    else:
                        st.info("Audit functionality unavailable")

            with dev_tabs[3]:
                log_path = Path("logchain_main.log")
                if not log_path.exists():
                    log_path = Path("remix_logchain.log")
                if log_path.exists():
                    try:
                        lines = log_path.read_text().splitlines()[-100:]
                        st.text("\n".join(lines))
                    except Exception as exc:
                        st.error(f"Log read failed: {exc}")
                else:
                    st.info("No log file found")

            with dev_tabs[4]:
                event_json = st.text_area(
                    "Event JSON", value="{}", height=150, key="inject_event"
                )
                if st.button("Process Event"):
                    if agent:
                        try:
                            event = json.loads(event_json or "{}")
                            agent.process_event(event)
                            st.success("Event processed")
                        except Exception as exc:
                            st.error(f"Event failed: {exc}")
                    else:
                        st.info("Agent unavailable")

            with dev_tabs[5]:
                st.write("Available agents:", list(AGENT_REGISTRY.keys()))
                if cosmic_nexus:
                    st.write(
                        "Sub universes:",
                        list(getattr(cosmic_nexus, "sub_universes", {}).keys()),
                    )
                if (
                    agent
                    and InMemoryStorage
                    and isinstance(agent.storage, InMemoryStorage)
                ):
                    st.write(
                        f"Users: {len(agent.storage.users)} / Coins: {len(agent.storage.coins)}"
                    )
                elif agent:
                    try:
                        user_count = len(agent.storage.get_all_users())
                    except Exception:
                        user_count = "?"
                    st.write(f"User count: {user_count}")

            with dev_tabs[6]:
                flow_txt = st.text_area(
                    "Agent Flow JSON",
                    "[]",
                    height=150,
                    key="flow_json",
                )
                if st.button("Run Flow"):
                    try:
                        steps = json.loads(flow_txt or "[]")
                        results = []
                        for step in steps:
                            a_name = step.get("agent")
                            agent_cls = AGENT_REGISTRY.get(a_name, {}).get("class")
                            evt = step.get("event", {})
                            if agent_cls:
                                backend_fn = get_backend("dummy")
                                a = agent_cls(llm_backend=backend_fn)
                                results.append(a.process_event(evt))
                        st.json(results)
                    except Exception as exc:
                        st.error(f"Flow execution failed: {exc}")

    if run_clicked or rerun_clicked:
        if run_clicked:
            if validations_input.strip():
                try:
                    data = json.loads(validations_input)
                    st.session_state["validations_json"] = json.dumps(data, indent=2)
                except json.JSONDecodeError as exc:
                    alert(f"Invalid JSON: {exc}", "error")
                    st.stop()
            elif demo_mode:
                try:
                    with open(sample_path) as f:
                        data = json.load(f)
                except FileNotFoundError:
                    alert("Demo file not found, using default dataset.", "warning")
                    data = {
                        "validations": [{"validator": "A", "target": "B", "score": 0.9}]
                    }
                st.session_state["validations_json"] = json.dumps(data, indent=2)
            elif uploaded_file is not None:
                data = json.load(uploaded_file)
                st.session_state["validations_json"] = json.dumps(data, indent=2)
            else:
                alert("Please upload a file, paste JSON, or enable demo mode.", "error")
                st.stop()
        else:
            try:
                data = json.loads(st.session_state.get("validations_json", ""))
            except Exception as exc:
                alert(f"Stored validations invalid: {exc}", "error")
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
            alert(f"Invalid payload: {exc}", "error")
        else:
            backend_fn = get_backend(backend_choice.lower(), api_key or None)
            if backend_fn is None:
                alert("Invalid backend selected", "error")
                st.session_state["agent_output"] = None
                st.stop()
            agent_cls = AGENT_REGISTRY.get(agent_choice, {}).get("class")
            if agent_cls is None:
                alert("Unknown agent selected", "error")
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
                    alert(f"Agent error: {exc}", "error")

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
        rfc_index: dict[str, dict[str, Any]] = {}
        for path in rfc_paths:
            text = path.read_text()
            summary = parse_summary(text)
            entry = {
                "id": path.stem,
                "summary": summary,
                "text": text,
                "path": path,
            }
            rfc_entries.append(entry)
            rfc_index[path.stem.lower()] = entry

        diary_mentions: dict[str, list[int]] = {str(e["id"]): [] for e in rfc_entries}
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
                    diary_mentions.setdefault(str(rfc["id"]), []).append(i)
                    continue
                keywords = {
                    w.strip(".,()[]{}:").lower()
                    for w in str(rfc["summary"]).split()
                    if len(w) > 4
                }
                if any(k in note_lower for k in keywords):
                    diary_mentions.setdefault(str(rfc["id"]), []).append(i)

        for rfc in rfc_entries:
            if (
                filter_text
                and filter_text.lower() not in rfc["summary"].lower()
                and filter_text.lower() not in rfc["id"].lower()
            ):
                continue
            mentions = diary_mentions.get(str(rfc["id"]), [])
            heading = f"<mark>{rfc['id']}</mark>" if mentions else rfc["id"]
            st.markdown(f"### {heading}", unsafe_allow_html=True)
            st.write(summarize_text(str(rfc["summary"])))
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

    if st.session_state.get("governance_view"):
        tabs = st.tabs(
            [
                "Proposal Hub",
                "Governance",
                "Agent Ops",
                "Logs",
            ]
        )
        with tabs[0]:
            render_proposals_tab()
        with tabs[1]:
            render_governance_tab()
        with tabs[2]:
            render_agent_ops_tab()
        with tabs[3]:
            render_logs_tab()
    else:
        st.info("Enable Governance View in the sidebar to see governance features.")


def main() -> None:
    header("superNova_2177 Validation Analyzer", layout="wide")
    tab1, tab2, tab3, tab4 = st.tabs(["Validation", "Friends", "Votes", "Agents"])
    with tab1:
        render_validation_ui()
    with tab2:
        render_social_tab()
    with tab3:
        render_voting_tab()
    with tab4:
        render_agent_insights_tab()
if __name__ == "__main__":
    logger.info("\u2705 Streamlit UI started. Launching main()...")
    print("Starting Streamlit UI...", file=sys.stderr)
    try:
        main()
    except Exception:
        logger.exception("UI startup failed")
        print("Startup failed", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise
    else:
        st.success("\u2705 UI Booted")
        print("UI Booted", file=sys.stderr)
    except Exception as exc:
        logger.exception("Startup failed")
        print(f"Startup failed: {exc}", file=sys.stderr)

