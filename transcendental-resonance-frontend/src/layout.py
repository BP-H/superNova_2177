from nicegui import ui, element

from utils.styles import set_theme, get_theme_name


def toggle_theme() -> None:
    """Switch between light and dark themes."""
    current = get_theme_name()
    new_name = "light" if current == "dark" else "dark"
    set_theme(new_name)


def build_layout() -> element.Element:
    """Construct the persistent header and navigation drawer."""
    drawer = ui.left_drawer().classes("bg-gray-900 text-white")
    with drawer:
        links = [
            ("Profile", "/profile"),
            ("VibeNodes", "/vibenodes"),
            ("Groups", "/groups"),
            ("Events", "/events"),
            ("Messages", "/messages"),
            ("Proposals", "/proposals"),
            ("Notifications", "/notifications"),
            ("Music", "/music"),
            ("Network", "/network"),
            ("Status", "/status"),
            ("System Insights", "/system-insights"),
            ("Upload", "/upload"),
        ]
        for label, path in links:
            ui.link(label, path).classes("block px-4 py-2")

    header = ui.header().classes("items-center justify-between")
    with header:
        ui.button(icon="menu", on_click=drawer.toggle).props("flat color=white")
        ui.label("Transcendental Resonance").classes("text-lg font-bold")
        ui.button("Toggle Theme", on_click=toggle_theme).props("flat")

    return header
