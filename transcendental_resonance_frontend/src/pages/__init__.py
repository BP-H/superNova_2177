"""Lazy-loading access to page modules for the Transcendental Resonance frontend."""

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

__all__ = [
    "login_page",
    "register_page",
    "profile_page",
    "vibenodes_page",
    "explore_page",
    "groups_page",
    "events_page",
    "proposals_page",
    "notifications_page",
    "messages_page",
    "ai_assist_page",
    "upload_page",
    "music_page",
    "status_page",
    "network_page",
    "system_insights_page",
    "forks_page",
    "validator_graph_page",
    "debug_panel_page",
]


def __getattr__(name):
    if name in __all__:
        module = __import__(f"pages.{name}", fromlist=[name])
        return getattr(module, name)
    raise AttributeError(name)
