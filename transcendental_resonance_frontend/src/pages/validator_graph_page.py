# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Validator graph visualization page using Plotly JS."""

import json

from nicegui import ui
from utils.api import TOKEN, api_call
from utils.layout import page_container, navigation_bar
from utils.styles import get_theme

from .login_page import login_page


@ui.page("/validator-graphs")
async def validator_graph_page():
    """Display validator network graphs."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label("Validator Graphs").classes("text-2xl font-bold mb-4").style(
            f'color: {THEME["accent"]};'
        )

        layout_select = ui.select(["random", "circle"], value="random").classes(
            "w-full mb-2"
        )
        try:
            stored = ui.run_javascript(
                "localStorage.getItem('validator_layout')",
                respond=True,
            )
            if isinstance(stored, str) and stored in ["random", "circle"]:
                layout_select.value = stored
        except Exception:
            stored = None  # nosec - localStorage access may fail during testing

        def _on_layout_change() -> None:
            ui.run_javascript(
                f"localStorage.setItem('validator_layout', '{layout_select.value}')"
            )
            ui.run_async(refresh_graph())

        layout_select.on("change", lambda _: _on_layout_change())

        filter_input = ui.input("Filter by label").classes("w-full mb-2")
        weight_slider = ui.slider(min=0, max=1, value=0, step=0.1).classes(
            "w-full mb-4"
        )
        weight_label = ui.label(f"Min Weight: {weight_slider.value}").classes("mb-4")
        weight_slider.on(
            "update:model-value",
            lambda e: weight_label.set_text(f"Min Weight: {e.value}"),
        )
        weight_slider.on("change", lambda _: ui.run_async(refresh_graph()))

        graph_area = ui.html("").classes("w-full h-96")

        async def refresh_graph() -> None:
            analysis = await api_call("GET", "/network-analysis/")
            if not analysis:
                return
            nodes = analysis.get("nodes", [])
            edges = analysis.get("edges", [])

            threshold = weight_slider.value or 0
            if threshold:
                edges = [e for e in edges if e.get("strength", 1) >= threshold]

            filt = (filter_input.value or "").strip().lower()
            if filt:
                nodes = [n for n in nodes if filt in str(n.get("label", "")).lower()]
            ids = {n["id"] for n in nodes}
            edges = [e for e in edges if e["source"] in ids and e["target"] in ids]

            graph_html = f"""
            <div id='validator_graph'></div>
            <script src='https://cdn.plot.ly/plotly-2.20.0.min.js'></script>
            <script>
            const nodes = {json.dumps(nodes)};
            const edges = {json.dumps(edges)};
            const layoutType = '{layout_select.value}';
            function getPositions() {{
                const positions = {{}};
                if(layoutType === 'circle') {{
                    const step = 2*Math.PI/nodes.length;
                    nodes.forEach((n,i)=>positions[n.id] = [Math.cos(i*step), Math.sin(i*step)]);
                }} else {{
                    nodes.forEach(n=>positions[n.id] = [Math.random()*2-1, Math.random()*2-1]);
                }}
                return positions;
            }}
            const pos = getPositions();
            const edge_x = [], edge_y = [];
            edges.forEach(e=>{{
                const s = pos[e.source];
                const t = pos[e.target];
                edge_x.push(s[0], t[0], null);
                edge_y.push(s[1], t[1], null);
            }});
            const node_x = [], node_y = [], texts = [];
            nodes.forEach(n=>{{
                const p = pos[n.id];
                node_x.push(p[0]);
                node_y.push(p[1]);
                texts.push(n.label);
            }});
            const traces = [
              {{x: edge_x, y: edge_y, mode: 'lines', line: {{color:'#888', width:1}}, hoverinfo:'none'}},
              {{x: node_x, y: node_y, mode: 'markers+text', text: texts,
                textposition: 'top center', marker: {{size:10, color:'#1f77b4'}}}}
            ];
            const layout = {{showlegend:false, xaxis:{{visible:false}}, yaxis:{{visible:false}}}};
            Plotly.newPlot('validator_graph', traces, layout);
            </script>
            """
            graph_area.set_content(graph_html)

        ui.button("Update", on_click=refresh_graph).classes("mb-4").style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )
        filter_input.on("change", lambda _: ui.run_async(refresh_graph()))
        await refresh_graph()
