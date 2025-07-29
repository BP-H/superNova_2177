"""Unified feed combining VibeNodes, Events, and Notifications.

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""

from nicegui import ui

from utils.api import TOKEN, api_call
from utils.layout import page_container, navigation_bar
from utils.styles import get_theme
from utils.features import quick_post_button, skeleton_loader, swipeable_glow_card
from quantum_futures import generate_speculative_futures, DISCLAIMER

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
        ui.label('Feed').classes('text-2xl font-bold mb-2').style(
            f'color: {theme["accent"]};'
        )

        simulation_switch = ui.switch('Enable Simulation View', value=False).classes('mb-4')
        simulation_switch.on('change', lambda _: ui.run_async(refresh_feed()))

        feed_column = ui.column().classes('w-full')

        post_dialog = ui.dialog()
        with post_dialog:
            with ui.card():
                ui.label('Compose new Vibe').classes('text-lg font-bold')
                ui.textarea('What\'s on your mind?').classes('w-full mb-2')
                ui.button('Post').on('click', post_dialog.close)

        quick_post_button(lambda: post_dialog.open())

        async def refresh_feed() -> None:
            if feed_column:
                feed_column.clear()
                with feed_column:
                    skeleton_loader()

            try:
                vibenodes = await api_call('GET', '/vibenodes/') or []
                events = await api_call('GET', '/events/') or []
                notifs = await api_call('GET', '/notifications/') or []
            except Exception:
                ui.notify('Failed to load feed', color='negative')
                return

            if feed_column:
                feed_column.clear()

            if not any([vibenodes, events, notifs]):
                ui.label('Nothing to show yet').classes('text-sm opacity-50')
                return

            for vn in vibenodes:
                with feed_column:
                    with swipeable_glow_card().classes('w-full mb-2').style('background: #1e1e1e;'):
                        ui.label('VibeNode').classes('text-sm font-bold')
                        ui.label(vn.get('description', '')).classes('text-sm')
                        ui.link('View', f"/vibenodes/{vn['id']}")
                        if simulation_switch.value:
                            futures = await generate_speculative_futures(vn)
                            with ui.expansion('Speculative futures', value=False).classes('w-full mt-2'):
                                for fut in futures:
                                    ui.markdown(fut['text']).classes('text-sm italic')
                                    ui.markdown(DISCLAIMER).classes('text-xs text-orange-5')
            for ev in events:
                with feed_column:
                    with swipeable_glow_card().classes('w-full mb-2').style('background: #1e1e1e;'):
                        ui.label('Event').classes('text-sm font-bold')
                        ui.label(ev.get('description', '')).classes('text-sm')
                        ui.link('View', f"/events/{ev['id']}")
                        if simulation_switch.value:
                            futures = await generate_speculative_futures(ev)
                            with ui.expansion('Speculative futures', value=False).classes('w-full mt-2'):
                                for fut in futures:
                                    ui.markdown(fut['text']).classes('text-sm italic')
                                    ui.markdown(DISCLAIMER).classes('text-xs text-orange-5')
            for n in notifs:
                with feed_column:
                    with swipeable_glow_card().classes('w-full mb-2').style('background: #1e1e1e;'):
                        ui.label('Notification').classes('text-sm font-bold')
                        ui.label(n.get('message', '')).classes('text-sm')
                        ui.link('View', f"/notifications/{n['id']}")
                        if simulation_switch.value:
                            futures = await generate_speculative_futures(n)
                            with ui.expansion('Speculative futures', value=False).classes('w-full mt-2'):
                                for fut in futures:
                                    ui.markdown(fut['text']).classes('text-sm italic')
                                    ui.markdown(DISCLAIMER).classes('text-xs text-orange-5')

        await refresh_feed()

        # --- Quick Post Floating Action Button ---
        post_dialog = ui.dialog()
        with post_dialog:
            with ui.card().classes('w-full p-4'):
                post_input = ui.textarea("What's on your mind?").classes('w-full mb-2')

                async def submit_post() -> None:
                    data = {'description': post_input.value}
                    resp = await api_call('POST', '/vibenodes/', data)
                    if resp:
                        ui.notify('Posted!', color='positive')
                        post_input.value = ''
                        if post_dialog.open:
                            post_dialog.close()
                        await refresh_feed()
                    else:
                        ui.notify('Failed to post', color='negative')

                ui.button('Post', on_click=submit_post).classes('w-full').style(
                    f'background: {theme["accent"]}; color: {theme["background"]};'
                )

        ui.button(icon='add', on_click=post_dialog.open).props(
            'fab fixed bottom-right'
        )
