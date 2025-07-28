# 3D Viewer

This folder provides a very small demo that renders a network graph using D3.js.
It loads `network.json` and displays the nodes and edges with a force directed
layout.

## Quick start

1. Serve the contents of this directory with any static HTTP server. A quick
   approach is:

   ```bash
   cd docs/3d_viewer
   python -m http.server 8000
   ```

2. Open `http://localhost:8000` in your browser. The included `render.js`
   automatically fetches `network.json` and visualises it.

Edit `network.json` to experiment with your own nodes and edges. Each node should
have a unique `id` and each edge should reference the node ids with `source` and
`target` fields.
