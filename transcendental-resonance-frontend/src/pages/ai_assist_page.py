"""AI assistance for VibeNodes."""

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from .login_page import login_page
from utils.layout import header


@ui.page('/ai-assist/{vibenode_id}')
async def ai_assist_page(vibenode_id: int):
    """Get AI-generated help for a specific VibeNode."""
    if not TOKEN:
        ui.open(login_page)
        return
    header()
    THEME = get_theme()
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('AI Assist').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        prompt = ui.textarea('Prompt for AI').classes('w-full mb-2')

        async def get_ai_response():
            data = {'prompt': prompt.value}
            resp = api_call('POST', f'/ai-assist/{vibenode_id}', data)
            if resp:
                ui.label('AI Response:').classes('mb-2')
                ui.label(resp['response']).classes('text-sm break-words')

        ui.button('Get AI Help', on_click=get_ai_response).classes('w-full').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )
