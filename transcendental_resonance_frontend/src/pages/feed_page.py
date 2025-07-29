"""Unified feed combining VibeNodes, Events, and Notifications."""

from nicegui import ui

from utils.api import TOKEN, api_call
from utils.layout import page_container, navigation_bar
from utils.styles import get_theme
from components import emoji_toolbar, render_media_block
from components.common import standard_card, loading_skeleton

from .login_page import login_page


@ui.page('/feed')
async def feed_page() -> None:
    """Display a combined feed of recent activity."""
    if not TOKEN:
        ui.open(login_page)
        return

    theme = get_theme()
    with page_container(theme):
        if TOKEN:
            navigation_bar()
        ui.label('Feed').classes('text-2xl font-bold mb-4').style(
            f'color: {theme["accent"]};'
        )

        with ui.card().classes('w-full mb-4').style(
            'border: 1px solid #333; background: #1e1e1e;'
        ):
            post_type = ui.select(['text', 'image', 'video'], value='text').props(
                'dense'
            ).classes('w-24 mb-2')
            post_input = ui.textarea('Share something...').classes('w-full mb-2')
            emoji_toolbar(post_input)
            preview = ui.markdown().classes('w-full mb-2')
            post_input.on('input', lambda e: preview.set_content(post_input.value))

            async def publish_post() -> None:
                data = {'type': post_type.value, 'content': post_input.value}
                resp = await api_call('POST', '/posts/', data, return_error=True)
                if resp and not resp.get('error'):
                    ui.notify('Posted!', color='positive')
                    post_input.value = ''
                    await refresh_feed()
                else:
                    ui.notify('Failed to post', color='negative')

            ui.button('Publish', on_click=lambda: ui.run_async(publish_post())).style(
                f'background: {theme["primary"]}; color: {theme["text"]};'
            ).classes('w-full')

        feed_column = ui.column().classes('w-full')

        async def refresh_feed() -> None:
            feed_column.clear()
            for _ in range(3):
                loading_skeleton()

            vibenodes = await api_call('GET', '/vibenodes/') or []
            events = await api_call('GET', '/events/') or []
            notifs = await api_call('GET', '/notifications/') or []

            feed_column.clear()
            for vn in vibenodes:
                with feed_column:
                    with standard_card():
                        ui.label('VibeNode').classes('text-sm font-bold')
                        ui.label(vn.get('description', '')).classes('text-sm')
                        if vn.get('media_url'):
                            render_media_block(vn['media_url'], vn.get('media_type', ''))
                        ui.link('View', f"/vibenodes/{vn['id']}")
            for ev in events:
                with feed_column:
                    with standard_card():
                        ui.label('Event').classes('text-sm font-bold')
                        ui.label(ev.get('description', '')).classes('text-sm')
                        if ev.get('media_url'):
                            render_media_block(ev['media_url'], ev.get('media_type', ''))
                        ui.link('View', f"/events/{ev['id']}")
            for n in notifs:
                with feed_column:
                    with standard_card():
                        ui.label('Notification').classes('text-sm font-bold')
                        ui.label(n.get('message', '')).classes('text-sm')
                        ui.link('View', f"/notifications/{n['id']}")

        await refresh_feed()
