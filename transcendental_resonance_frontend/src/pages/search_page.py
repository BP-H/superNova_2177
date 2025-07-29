from __future__ import annotations

from typing import Dict, List

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.layout import page_container
from utils.styles import get_theme
from .login_page import login_page


@ui.page('/search')
async def search_page(q: str | None = None) -> None:
    """Search across VibeNodes, groups, and events."""
    if not TOKEN:
        ui.open(login_page)
        return

    query = q or ''
    THEME = get_theme()
    with page_container(THEME):
        search_input = ui.input('Search', value=query).classes('w-full mb-4')
        async def submit() -> None:
            ui.open(f'/search?q={search_input.value}')
        search_input.on('keydown.enter', lambda _: ui.run_async(submit()))
        ui.button('Search', on_click=submit).classes('mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        results_container = ui.column().classes('w-full')

        if query:
            results = await api_call('GET', '/search', {'q': query}) or []
            grouped: Dict[str, List[dict]] = {}
            for item in results:
                grouped.setdefault(item.get('type', 'other'), []).append(item)

            for kind, items in grouped.items():
                ui.label(kind.title()).classes('text-xl font-bold mt-2').style(
                    f'color: {THEME["accent"]};'
                )
                for item in items:
                    name = item.get('name') or item.get('title', 'Unnamed')
                    link_target = '#'
                    if kind == 'vibenode':
                        link_target = f"/vibenodes?id={item.get('id')}"
                    elif kind == 'group':
                        link_target = f"/groups?id={item.get('id')}"
                    elif kind == 'event':
                        link_target = f"/events?id={item.get('id')}"
                    ui.link(name, link_target).classes('block mb-1')

