"""Messaging system page."""

from nicegui import ui
from utils.api import TOKEN, api_call
from utils.layout import page_container
from utils.styles import get_theme

from .login_page import login_page


@ui.page("/messages")
async def messages_page():
    """Send and view messages."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        ui.label("Messages").classes("text-2xl font-bold mb-4").style(
            f'color: {THEME["accent"]};'
        )

        recipient = ui.input("Recipient Username").classes("w-full mb-2")
        content = ui.textarea("Message").classes("w-full mb-2")

        async def send_message():
            data = {"content": content.value}
            resp = await api_call("POST", f"/messages/{recipient.value}", data)
            if resp:
                ui.notify("Message sent!", color="positive")
                await refresh_messages()

        ui.button("Send", on_click=send_message).classes("w-full mb-4").style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        messages_list = ui.column().classes("w-full")

        async def refresh_messages():
            messages = await api_call("GET", "/messages/") or []
            messages_list.clear()
            for m in messages:
                with messages_list:
                    with (
                        ui.card()
                        .classes("w-full mb-2")
                        .style("border: 1px solid #333; background: #1e1e1e;")
                    ):
                        ui.label(f"From: {m['sender_id']}").classes("text-sm")
                        ui.label(m["content"]).classes("text-sm")

        await refresh_messages()
        ui.timer(30, lambda: ui.run_async(refresh_messages()))
