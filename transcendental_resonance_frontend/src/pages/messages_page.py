# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Messaging system page."""

from nicegui import ui
from utils.api import TOKEN, api_call, listen_ws, send_ws
from utils.realtime_utils import get_username, get_user_cached, humanize_timestamp
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
        content.on(
            "input",
            lambda _: ui.run_async(
                send_ws({"type": "typing", "recipient": recipient.value})
            ),
        )
        typing_label = ui.label().classes("text-sm italic mb-2")

        async def send_message():
            data = {"content": content.value}
            resp = await api_call("POST", f"/messages/{recipient.value}", data)
            if resp:
                ui.notify("Message sent!", color="positive")
                content.value = ""
                await refresh_messages()

        ui.button("Send", on_click=send_message).classes("w-full mb-4").style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        messages_list = ui.column().classes("w-full")

        edit_dialog = ui.dialog()
        with edit_dialog:
            with ui.card().classes("w-full p-4"):
                edit_input = ui.textarea().classes("w-full mb-2")

                async def save_edit() -> None:
                    if edit_message_id is None:
                        return
                    resp = await api_call(
                        "PUT",
                        f"/messages/{edit_message_id}",
                        {"content": edit_input.value},
                    )
                    if resp:
                        ui.notify("Message updated", color="positive")
                        edit_dialog.close()
                        await refresh_messages()

                ui.button("Save", on_click=save_edit).style(
                    f"background: {THEME['primary']}; color: {THEME['text']};"
                )

        edit_message_id: int | None = None

        async def open_edit(m: dict) -> None:
            nonlocal edit_message_id
            edit_message_id = m["id"]
            edit_input.value = m["content"]
            edit_dialog.open()

        async def refresh_messages():
            messages = await api_call("GET", "/messages/") or []
            messages_list.clear()
            for m in messages:
                username = await get_username(m.get("sender_id"))
                user_data = await get_user_cached(m.get("sender_id")) or {}
                avatar_url = user_data.get("avatar_url")
                ts = humanize_timestamp(m.get("timestamp") or m.get("created_at", ""))
                with messages_list:
                    with (
                        ui.card()
                        .classes("w-full mb-2")
                        .style(f"border: 1px solid #333; background: {THEME['background']};")
                    ):
                        with ui.row().classes("items-start justify-between"):
                            ui.image(
                                avatar_url or "https://via.placeholder.com/40"
                            ).classes("w-8 h-8 rounded-full mr-2")
                            with ui.column().classes("grow"):
                                with ui.row().classes("items-center justify-between"):
                                    ui.label(username).classes("text-sm font-bold")
                                    ui.label(ts).classes("text-xs text-gray-400")
                                ui.label(m["content"]).classes("text-sm")
                            ui.button(
                                on_click=lambda msg=m: ui.run_async(open_edit(msg)),
                                icon="edit",
                            ).props("flat")

        await refresh_messages()
        ui.timer(30, lambda: ui.run_async(refresh_messages()))

        typing_timers: dict[int, ui.timer] = {}

        async def handle_event(event: dict) -> None:
            etype = event.get("type")
            if etype == "message":
                await refresh_messages()
            elif etype == "typing":
                sender = event.get("sender_id")
                username = await get_username(sender)
                typing_label.text = f"{username} is typing..."

                def clear() -> None:
                    typing_label.text = ""

                if sender in typing_timers:
                    typing_timers[sender].stop()
                typing_timers[sender] = ui.timer(2, clear, once=True)

        ui.run_async(listen_ws(handle_event))
