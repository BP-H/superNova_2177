# Tank Merge Protocol

This project uses **tanks** to encapsulate optional modules that expose UI routes.
To keep route registration deterministic each tank describes itself via a
`TankManifest` and registers with the global `TankRegistry`.

A manifest lists the available routes and whether the tank mutates shared state.
When a tank is imported during startup its manifest is registered allowing
introspection via `TankRegistry.list_routes()`.

Future merges should register new routes using
`register_route_once(name, handler)` from `frontend_bridge`. This ensures that
multiple imports of a tank will not overwrite existing handlers.
