"""VibeNodes creation and listing."""

from nicegui import ui

from utils.api import api_call, THEME, TOKEN
from .login_page import login_page


@ui.page('/vibenodes')
async def vibenodes_page():
    """Create and display VibeNodes."""
    if not TOKEN:
        ui.open(login_page)
        return

    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('VibeNodes').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        name = ui.input('Name').classes('w-full mb-2')
        description = ui.textarea('Description').classes('w-full mb-2')
        media_type = ui.select(
            ['text', 'image', 'video', 'audio', 'music', 'mixed'],
            value='text',
        ).classes('w-full mb-2')
        tags = ui.input('Tags (comma-separated)').classes('w-full mb-2')
        parent_id = ui.input('Parent VibeNode ID (optional)').classes('w-full mb-2')

        async def create_vibenode():
            data = {
                'name': name.value,
                'description': description.value,
                'media_type': media_type.value,
                'tags': [t.strip() for t in tags.value.split(',')] if tags.value else None,
                'parent_vibenode_id': int(parent_id.value) if parent_id.value else None,
            }
            resp = await api_call('POST', '/vibenodes/', data)
            if resp:
                ui.notify('VibeNode created!', color='positive')
                await refresh_vibenodes()

        ui.button('Create VibeNode', on_click=create_vibenode).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        vibenodes_list = ui.column().classes('w-full')

        async def refresh_vibenodes():
            vibenodes = await api_call('GET', '/vibenodes/') or []
            vibenodes_list.clear()
            for vn in vibenodes:
                with vibenodes_list:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label(vn['name']).classes('text-lg')
                        ui.label(vn['description']).classes('text-sm')
                        ui.label(f"Likes: {vn.get('likes_count', 0)}").classes('text-sm')
                        async def like_fn(vn_id=vn['id']):
                            await api_call('POST', f'/vibenodes/{vn_id}/like')
                            await refresh_vibenodes()
                        ui.button('Like/Unlike', on_click=like_fn).style(
                            f'background: {THEME["accent"]}; color: {THEME["background"]};'
                        )

        await refresh_vibenodes()
