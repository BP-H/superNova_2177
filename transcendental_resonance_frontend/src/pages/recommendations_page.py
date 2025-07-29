# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Recommendations discovery page."""

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from utils.layout import page_container, navigation_bar
from utils.features import skeleton_loader
from .login_page import login_page


@ui.page('/discover')
async def recommendations_page():
    """Fetch and display recommended users, groups, or events."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label('Discover').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        rec_list = ui.column().classes('w-full')

        async def refresh_recs() -> None:
            recs = await api_call('GET', '/recommendations')
            if recs is None:
                ui.notify('Failed to load data', color='negative')
                return
            rec_list.clear()
            for rec in recs:
                with rec_list:
                    with ui.card().classes('w-full mb-2').style(
                        'border: 1px solid #333; background: #1e1e1e;'
                    ):
                        name = rec.get('name') or rec.get('username', 'Unknown')
                        ui.label(name).classes('text-lg')
                        desc = rec.get('description') or rec.get('bio')
                        if desc:
                            ui.label(desc).classes('text-sm')
                        rtype = rec.get('type')
                        if rtype == 'user':
                            async def follow_fn(u=rec.get('id')):
                                await api_call('POST', f'/users/{u}/follow')
                                await refresh_recs()
                            ui.button('Follow/Unfollow', on_click=follow_fn).style(
                                f'background: {THEME["accent"]}; color: {THEME["background"]};'
                            )
                        elif rtype == 'group':
                            async def join_fn(g=rec.get('id')):
                                await api_call('POST', f'/groups/{g}/join')
                                await refresh_recs()
                            ui.button('Join/Leave', on_click=join_fn).style(
                                f'background: {THEME["accent"]}; color: {THEME["background"]};'
                            )
                        elif rtype == 'event':
                            async def attend_fn(e=rec.get('id')):
                                await api_call('POST', f'/events/{e}/attend')
                                await refresh_recs()
                            ui.button('Attend/Leave', on_click=attend_fn).style(
                                f'background: {THEME["accent"]}; color: {THEME["background"]};'
                            )

        await refresh_recs()
