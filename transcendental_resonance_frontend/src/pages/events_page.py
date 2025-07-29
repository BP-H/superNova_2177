"""Event management page."""

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from utils.layout import page_container
from .login_page import login_page


@ui.page('/events')
async def events_page():
    """Create and manage events."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        ui.label('Events').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        search_query = ui.input('Search').classes('w-full mb-2')
        sort_select = ui.select(['name', 'date'], value='name').classes('w-full mb-4')

        e_name = ui.input('Event Name').classes('w-full mb-2')
        e_desc = ui.textarea('Description').classes('w-full mb-2')
        e_start = ui.input('Start Time (YYYY-MM-DDTHH:MM)').classes('w-full mb-2')
        group_id = ui.input('Group ID').classes('w-full mb-2')

        async def create_event():
            gid_value = group_id.value
            if gid_value and gid_value.isdigit():
                gid = int(gid_value)
            else:
                gid = None
            data = {
                'name': e_name.value,
                'description': e_desc.value,
                'start_time': e_start.value,
                'group_id': gid,
            }
            resp = await api_call('POST', '/events/', data)
            if resp:
                ui.notify('Event created!', color='positive')
                await refresh_events()

        ui.button('Create Event', on_click=create_event).classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        loading = ui.spinner().classes('m-4')
        loading.visible = False
        events_list = ui.column().classes('w-full')

        async def refresh_events():
            loading.visible = True
            params = {}
            if search_query.value:
                params['search'] = search_query.value
            if sort_select.value:
                params['sort'] = sort_select.value
            events = await api_call('GET', '/events/', params) or []
            if search_query.value:
                events = [e for e in events if search_query.value.lower() in e['name'].lower()]
            if sort_select.value:
                if sort_select.value == 'name':
                    events.sort(key=lambda x: x.get('name', ''))
                elif sort_select.value == 'date':
                    events.sort(key=lambda x: x.get('start_time', ''))
            events_list.clear()
            for e in events:
                with events_list:
                    with ui.card().classes('w-full mb-2').style('border: 1px solid #333; background: #1e1e1e;'):
                        ui.label(e['name']).classes('text-lg')
                        ui.label(e['description']).classes('text-sm')
                        ui.label(f"Start: {e['start_time']}").classes('text-sm')
                        async def attend_fn(e_id=e['id']):
                            await api_call('POST', f'/events/{e_id}/attend')
                            await refresh_events()
                        ui.button('Attend/Leave', on_click=attend_fn).style(
                            f'background: {THEME["accent"]}; color: {THEME["background"]};'
                        )
            loading.visible = False

        await refresh_events()
