"""Group management page."""

from nicegui import ui

from utils.api import api_call, THEME, TOKEN
from .login_page import login_page


@ui.page('/groups')
async def groups_page():
    """Create and join groups."""
    if not TOKEN:
        ui.open(login_page)
        return

    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('Groups').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

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
            groups = await api_call('GET', '/groups/') or []
            groups_list.clear()
            for g in groups:
                with groups_list:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label(g['name']).classes('text-lg')
                        ui.label(g['description']).classes('text-sm')
                        async def join_fn(g_id=g['id']):
                            await api_call('POST', f'/groups/{g_id}/join')
                            await refresh_groups()
                        ui.button('Join/Leave', on_click=join_fn).style(
                            f'background: {THEME["accent"]}; color: {THEME["background"]};'
                        )

        await refresh_groups()
