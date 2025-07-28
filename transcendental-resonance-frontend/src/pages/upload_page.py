"""Media upload page."""

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from utils.layout import page_container
from .login_page import login_page


@ui.page('/upload')
async def upload_page():
    """Upload media files."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        ui.label('Upload Media').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        ui.upload(on_upload=lambda e: handle_upload(e.content, e.name)).classes('w-full mb-4')

        async def handle_upload(content, name):
            files = {'file': (name, content.read(), 'multipart/form-data')}
            resp = api_call('POST', '/upload/', files=files, method='multipart')
            if resp:
                ui.notify(f"Uploaded: {resp['media_url']}", color='positive')

        ui.label('Select file to upload').classes('text-center')
