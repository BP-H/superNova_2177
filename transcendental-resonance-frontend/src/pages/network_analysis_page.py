"""Network analysis visualization page."""

import json
from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from .login_page import login_page


@ui.page('/network')
async def network_page():
    """Display a graph of the user network."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('Network Analysis').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        nodes_label = ui.label().classes('mb-2')
        edges_label = ui.label().classes('mb-2')
        graph = ui.html('').classes('w-full h-96')

        async def refresh_network() -> None:
            analysis = api_call('GET', '/network-analysis/')
            if analysis:
                nodes_label.text = f"Nodes: {analysis['metrics']['node_count']}"
                edges_label.text = f"Edges: {analysis['metrics']['edge_count']}"
                graph_html = f"""
                <div id='network'></div>
                <script type='text/javascript' src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js'></script>
                <script type='text/javascript'>
                    var nodes = new vis.DataSet({json.dumps(analysis['nodes'])});
                    var edges = new vis.DataSet({json.dumps(analysis['edges'])});
                    var container = document.getElementById('network');
                    var data = {{nodes: nodes, edges: edges}};
                    var options = {{physics: {{enabled: true}}}};
                    var network = new vis.Network(container, data, options);
                </script>
                """
                graph.set_content(graph_html)

        await refresh_network()
        ui.timer(10, refresh_network)
