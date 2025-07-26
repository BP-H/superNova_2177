import importlib
import pages

PAGE_MODULES = {
    "login_page": "pages.login_page",
    "register_page": "pages.login_page",
    "profile_page": "pages.profile_page",
    "vibenodes_page": "pages.vibenodes_page",
    "groups_page": "pages.groups_page",
    "events_page": "pages.events_page",
    "proposals_page": "pages.proposals_page",
    "notifications_page": "pages.notifications_page",
    "messages_page": "pages.messages_page",
    "ai_assist_page": "pages.ai_assist_page",
    "upload_page": "pages.upload_page",
    "status_page": "pages.status_page",
    "network_page": "pages.network_analysis_page",
}


def test_pages_have_nicegui_path():
    for name in pages.__all__:
        module_path = PAGE_MODULES[name]
        module = importlib.reload(importlib.import_module(module_path))
        func = getattr(module, name)
        assert hasattr(func, "__nicegui_path__"), f"{name} missing __nicegui_path__"



