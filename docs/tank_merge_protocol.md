# Tank Merge Protocol

This repository uses a small routing layer to expose UI callbacks.  To keep
future merges sane each tank (module providing UI handlers) registers its routes
through `frontend_bridge.load_routes()` which delegates to the central
`tank_registry`.

## Guidelines

- New tanks should expose their handlers without side effects.
- Routes must be added to `load_routes()` via `register_route`.
- Use `register_route` only once per route. Existing names will log a warning
  but keep the first handler.
- Tests ensure all registered routes are unique and callable.
