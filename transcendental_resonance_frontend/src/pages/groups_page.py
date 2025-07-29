# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Group management page."""

from nicegui import ui

from utils.api import api_call, TOKEN, get_group_recommendations
from utils.styles import get_theme
from utils.layout import page_container, navigation_bar
from utils.features import skeleton_loader
from .login_page import login_page


@ui.page('/groups')
async def groups_page():
    """Create and join groups."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label('Groups').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        search_query = ui.input('Search').classes('w-full mb-2')
        sort_select = ui.select(['name', 'date'], value='name').classes('w-full mb-4')

        g_name = ui.input('Group Name').classes('w-full mb-2')
        g_desc = ui.textarea('Description').classes('w-full mb-2')

        async def create_group():
            data = {'name': g_name.value, 'description': g_desc.value}
            resp = await api_call('POST', '/groups/', data)
            if resp:
                ui.notify('Group created!', color='positive')
                await refresh_groups()

        ui.button('Create Group', on_click=create_group).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        groups_list = ui.column().classes('w-full')

        async def refresh_groups():
            params = {}
            if search_query.value:
                params['search'] = search_query.value
            if sort_select.value:
                params['sort'] = sort_select.value
            groups = await api_call('GET', '/groups/', params)
            if groups is None:
                ui.notify('Failed to load data', color='negative')
                return
            if search_query.value:
                groups = [g for g in groups if search_query.value.lower() in g['name'].lower()]
            if sort_select.value:
                if sort_select.value == 'name':
                    groups.sort(key=lambda x: x.get('name', ''))
                elif sort_select.value == 'date':
                    groups.sort(key=lambda x: x.get('created_at', ''))
            groups_list.clear()
            for g in groups:
                with groups_list:
                    with ui.card().classes('w-full mb-2').style(
                        f"border: 1px solid #333; background: {THEME['background']};"
                    ):
                        ui.label(g['name']).classes('text-lg')
                        ui.label(g['description']).classes('text-sm')
                        async def join_fn(g_id=g['id']):
                            await api_call('POST', f'/groups/{g_id}/join')
                            await refresh_groups()
                        ui.button('Join/Leave', on_click=join_fn).style(
                            f'background: {THEME["accent"]}; color: {THEME["background"]};'
                        )

        await refresh_groups()

        ui.label('You may like').classes('text-xl font-bold mt-4').style(
            f'color: {THEME["accent"]};'
        )
        suggestions = ui.column().classes('w-full')

        async def load_suggestions() -> None:
            recs = await get_group_recommendations()
            for g in recs:
                with suggestions:
                    with ui.card().classes('w-full mb-2').style(
                        f"border: 1px solid #333; background: {THEME['background']};"
                    ):
                        ui.label(g.get('name', 'Unknown')).classes('text-lg')
                        desc = g.get('description')
                        if desc:
                            ui.label(desc).classes('text-sm')

        await load_suggestions()
