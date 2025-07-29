# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Page to list universe forks and submit votes."""

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from utils.layout import page_container, navigation_bar
from .login_page import login_page


@ui.page('/forks')
async def forks_page() -> None:
    """Display forks and allow voting."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label('Universe Forks').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        fork_id = ui.input('Fork ID').classes('w-full mb-2')
        vote_value = ui.select(['yes', 'no'], value='yes').classes('w-full mb-2')

        async def submit_vote() -> None:
            data = {'fork_id': fork_id.value, 'vote': vote_value.value}
            resp = await api_call('POST', '/vote', data)
            if resp is not None:
                ui.notify('Vote submitted!', color='positive')
                await refresh_forks()
            else:
                ui.notify('Vote failed', color='negative')

        ui.button('Submit Vote', on_click=submit_vote).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        forks_list = ui.column().classes('w-full')

        async def refresh_forks() -> None:
            forks = await api_call('GET', '/forks') or []
            forks_list.clear()
            for f in forks:
                with forks_list:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label(f"ID: {f.get('id')}").classes('text-sm')
                        ui.label(f"Consensus: {f.get('consensus')}").classes('text-sm')

        await refresh_forks()

