"""VibeNodes creation and listing."""

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from utils.layout import page_container, nav_bar
from .login_page import login_page


@ui.page('/vibenodes')
async def vibenodes_page():
    """Create and display VibeNodes."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        with nav_bar(THEME):
            pass
        ui.label('VibeNodes').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        search_query = ui.input('Search').classes('w-full mb-2')
        sort_select = ui.select(['name', 'date'], value='name').classes('w-full mb-4')

        name = ui.input('Name').classes('w-full mb-2')
        description = ui.textarea('Description').classes('w-full mb-2')
        media_type = ui.select(
            ['text', 'image', 'video', 'audio', 'music', 'mixed'],
            value='text',
        ).classes('w-full mb-2')
        tags = ui.input('Tags (comma-separated)').classes('w-full mb-2')
        parent_id = ui.input('Parent VibeNode ID (optional)').classes('w-full mb-2')

        uploaded_media = {'url': None, 'type': None}

        async def handle_upload(content, name):
            files = {'file': (name, content.read(), 'multipart/form-data')}
            resp = await api_call('POST', '/upload/', files=files)
            if resp:
                uploaded_media['url'] = resp.get('media_url')
                uploaded_media['type'] = resp.get('media_type')
                ui.notify('Media uploaded', color='positive')
                if uploaded_media['type'] and uploaded_media['type'].startswith('image'):
                    ui.image(uploaded_media['url']).classes('w-full mb-2')

        ui.upload(on_upload=lambda e: ui.run_async(handle_upload(e.content, e.name))).classes('w-full mb-2')

        async def create_vibenode():
            data = {
                'name': name.value,
                'description': description.value,
                'media_type': uploaded_media.get('type') or media_type.value,
                'tags': [t.strip() for t in tags.value.split(',')] if tags.value else None,
                'parent_vibenode_id': int(parent_id.value) if parent_id.value else None,
            }
            if uploaded_media.get('url'):
                data['media_url'] = uploaded_media['url']
            resp = await api_call('POST', '/vibenodes/', data)
            if resp:
                ui.notify('VibeNode created!', color='positive')
                await refresh_vibenodes()

        ui.button('Create VibeNode', on_click=create_vibenode).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        vibenodes_list = ui.column().classes('w-full')

        async def refresh_vibenodes():
            params = {}
            if search_query.value:
                params['search'] = search_query.value
            if sort_select.value:
                params['sort'] = sort_select.value
            vibenodes = await api_call('GET', '/vibenodes/', params) or []
            if search_query.value:
                vibenodes = [vn for vn in vibenodes if search_query.value.lower() in vn['name'].lower()]
            if sort_select.value:
                if sort_select.value == 'name':
                    vibenodes.sort(key=lambda x: x.get('name', ''))
                elif sort_select.value == 'date':
                    vibenodes.sort(key=lambda x: x.get('created_at', ''))
            vibenodes_list.clear()
            for vn in vibenodes:
                with vibenodes_list:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label(vn['name']).classes('text-lg')
                        ui.label(vn['description']).classes('text-sm')
                        if vn.get('media_url'):
                            mtype = vn.get('media_type', '')
                            if mtype.startswith('image'):
                                ui.image(vn['media_url']).classes('w-full')
                            elif mtype.startswith('video'):
                                ui.video(vn['media_url']).classes('w-full')
                            elif mtype.startswith('audio') or mtype.startswith('music'):
                                ui.audio(vn['media_url']).classes('w-full')
                        ui.label(f"Likes: {vn.get('likes_count', 0)}").classes('text-sm')
                        async def like_fn(vn_id=vn['id']):
                            await api_call('POST', f'/vibenodes/{vn_id}/like')
                            await refresh_vibenodes()
                        ui.button('Like/Unlike', on_click=like_fn).style(
                            f'background: {THEME["accent"]}; color: {THEME["background"]};'
                        )
                        async def remix_fn(vn_data=vn):
                            name.value = vn_data['name']
                            description.value = vn_data['description']
                            parent_id.value = str(vn_data['id'])
                            ui.notify('Loaded remix draft', color='info')
                        ui.button('Remix', on_click=remix_fn).style(
                            f'background: {THEME["primary"]}; color: {THEME["text"]};'
                        )

        await refresh_vibenodes()
