from pathlib import Path
from typing import Any, cast
import streamlit as st


def summarize_text(text: str, max_len: int = 150) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def render_agent_insights_tab() -> None:
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
