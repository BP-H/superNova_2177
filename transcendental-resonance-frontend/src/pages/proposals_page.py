"""Governance proposals page."""

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from .login_page import login_page


@ui.page('/proposals')
async def proposals_page():
    """Create and vote on proposals."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('Proposals').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        p_title = ui.input('Title').classes('w-full mb-2')
        p_desc = ui.textarea('Description').classes('w-full mb-2')
        p_type = ui.select(['general', 'system_parameter_change'], value='general').classes('w-full mb-2')
        p_group_id = ui.input('Group ID (optional)').classes('w-full mb-2')

        async def create_proposal():
            data = {
                'title': p_title.value,
                'description': p_desc.value,
                'proposal_type': p_type.value,
                'group_id': int(p_group_id.value) if p_group_id.value else None,
            }
            resp = api_call('POST', '/proposals/', data)
            if resp:
                ui.notify('Proposal created!', color='positive')
                await refresh_proposals()

        ui.button('Create Proposal', on_click=create_proposal).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        proposals_list = ui.column().classes('w-full')

        async def refresh_proposals():
            proposals = api_call('GET', '/proposals/') or []
            proposals_list.clear()
            for p in proposals:
                with proposals_list:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label(p['title']).classes('text-lg')
                        ui.label(p['description']).classes('text-sm')
                        ui.label(f"Status: {p['status']}").classes('text-sm')
                        if p['status'] == 'open':
                            async def vote_yes(p_id=p['id']):
                                api_call('POST', f'/proposals/{p_id}/vote', {'vote': 'yes'})
                                await refresh_proposals()
                            async def vote_no(p_id=p['id']):
                                api_call('POST', f'/proposals/{p_id}/vote', {'vote': 'no'})
                                await refresh_proposals()
                            ui.row().classes('justify-between')
                            ui.button('Yes', on_click=vote_yes).style('background: green; color: white;')
                            ui.button('No', on_click=vote_no).style('background: red; color: white;')

        await refresh_proposals()
