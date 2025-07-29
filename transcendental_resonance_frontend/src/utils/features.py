from __future__ import annotations

"""Scaffolding components for upcoming UI features."""

try:  # pragma: no cover - allow import without NiceGUI installed
    from nicegui import ui
    from nicegui.element import Element
except Exception:  # pragma: no cover - fallback stubs for testing
    import types

    class Element:  # type: ignore
        pass

    def _dummy_element() -> Element:
        return Element()

    class _DummyUI:
        def button(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def card(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def left_drawer(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def switch(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def dialog(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def color_picker(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def overlay(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def tooltip(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def bottom_sheet(self, *args, **kwargs) -> Element:
            return _dummy_element()

        def skeleton(self, *args, **kwargs) -> Element:
            return _dummy_element()

    ui = _DummyUI()  # type: ignore


# ---------------------------------------------------------------------------
# Basic scaffolding functions
# ---------------------------------------------------------------------------

def quick_post_button(on_click) -> Element:
    """Floating action button opening the post dialog."""
    return ui.button(icon="add", on_click=on_click).props(
        "fab fixed bottom right bg-primary text-white"
    )


def swipeable_glow_card() -> Element:
    """Card placeholder with swipe handling and neon glow class."""
    card = ui.card().classes("glow-card")
    card.on("swipe", lambda _: None)
    return card


def notification_drawer() -> Element:
    """Sliding drawer for real-time notifications."""
    return ui.left_drawer().props("overlay")


def high_contrast_switch() -> Element:
    """Toggle switch for high contrast mode."""
    return ui.switch("High Contrast")


def shortcut_help_dialog(shortcuts: list[str] | None = None) -> Element:
    """Dialog listing keyboard shortcuts."""
    dlg = ui.dialog()
    with dlg:
        with ui.card():
            ui.label("Keyboard Shortcuts").classes("text-lg font-bold")
            if shortcuts:
                for s in shortcuts:
                    ui.label(s).classes("text-sm")
    return dlg


def theme_personalization_panel() -> Element:
    """Simple color picker for theme personalization."""
    return ui.color_picker()


def onboarding_overlay() -> Element:
    """Transient overlay shown on first login."""
    return ui.overlay("Welcome!").props("transition-fade").close_on_click(True)


def profile_popover() -> Element:
    """Popover stub showing quick profile info."""
    return ui.tooltip("profile")


def mobile_bottom_sheet() -> Element:
    """Bottom sheet for mobile actions."""
    return ui.bottom_sheet()


def skeleton_loader() -> Element:
    """Animated skeleton loader placeholder."""
    return ui.skeleton().classes("animate-pulse")


__all__ = [
    "quick_post_button",
    "swipeable_glow_card",
    "notification_drawer",
    "high_contrast_switch",
    "shortcut_help_dialog",
    "theme_personalization_panel",
    "onboarding_overlay",
    "profile_popover",
    "mobile_bottom_sheet",
    "skeleton_loader",
]
