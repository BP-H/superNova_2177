"""Media upload page."""

from nicegui import ui
import asyncio

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from utils.layout import page_container, navigation_bar
from .login_page import login_page


@ui.page('/upload')
async def upload_page():
    """Upload media files."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        if TOKEN:
            navigation_bar()
        ui.label('Upload Media').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        progress_container = ui.column().classes('w-full')

        async def handle_upload(event):
            with progress_container:
                progress = ui.linear_progress(value=0).classes('w-full mb-2')
            async def spin():
                while progress.value < 0.95:
                    await asyncio.sleep(0.1)
                    progress.value += 0.05
            spinner = asyncio.create_task(spin())
            files = {'file': (event.name, event.content.read(), 'multipart/form-data')}
            resp = await api_call('POST', '/upload/', files=files)
            spinner.cancel()
            progress.value = 1.0
            if resp:
                ui.notify(f"Uploaded: {resp['media_url']}", color='positive')

        ui.upload(multiple=True, auto_upload=True,
                  on_upload=lambda e: ui.run_async(handle_upload(e))) \
            .props('label=Drop files here') \
            .classes('w-full mb-4 border-2 border-dashed rounded-lg p-4')

        ui.label('Select or drop files to upload').classes('text-center mb-8')

        ui.label('Upload New Avatar').classes('text-xl font-bold mb-2').style(
            f'color: {THEME["accent"]};'
        )

        async def handle_avatar_upload(event):
            files = {'file': (event.name, event.content.read(), 'multipart/form-data')}
            resp = await api_call('POST', '/upload/avatar', files=files)
            if resp and resp.get('avatar_url'):
                await api_call('PUT', '/users/me', {'avatar_url': resp['avatar_url']})
                ui.notify('Avatar updated', color='positive')

        ui.upload(on_upload=lambda e: ui.run_async(handle_avatar_upload(e))) \
            .props('label=Choose avatar image') \
            .classes('w-full mb-4')
