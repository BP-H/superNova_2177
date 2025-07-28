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

        # ---- Node creation form ----
        node_id = ui.input('Node ID').classes('w-full mb-2')
        node_label = ui.input('Label').classes('w-full mb-2')
        node_type = ui.input('Type').classes('w-full mb-2')

        async def create_node() -> None:
            data = {
                'id': node_id.value,
                'label': node_label.value,
                'type': node_type.value,
            }
            resp = await api_call('POST', '/network-analysis/nodes', data)
            if resp is not None:
                ui.notify('Node created', color='positive')
                node_id.value = ''
                node_label.value = ''
                node_type.value = ''
                await refresh_network()

        ui.button('Add Node', on_click=create_node).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        # ---- Edge creation form ----
        edge_source = ui.input('Source ID').classes('w-full mb-2')
        edge_target = ui.input('Target ID').classes('w-full mb-2')
        edge_type = ui.input('Edge Type').classes('w-full mb-2')

        async def create_edge() -> None:
            data = {
                'source': edge_source.value,
                'target': edge_target.value,
                'type': edge_type.value,
            }
            resp = await api_call('POST', '/network-analysis/edges', data)
            if resp is not None:
                ui.notify('Edge created', color='positive')
                edge_source.value = ''
                edge_target.value = ''
                edge_type.value = ''
                await refresh_network()

        ui.button('Add Edge', on_click=create_edge).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        graph = ui.html('').classes('w-full h-96')

        async def refresh_network() -> None:
            analysis = await api_call('GET', '/network-analysis/')
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
