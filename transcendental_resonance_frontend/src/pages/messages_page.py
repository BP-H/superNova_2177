# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Messaging system page."""

from nicegui import ui
from utils.api import TOKEN, api_call, listen_ws
from utils.layout import page_container, navigation_bar
from components.emoji_toolbar import emoji_toolbar
from utils.safe_markdown import safe_markdown
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
        if TOKEN:
            navigation_bar()
        ui.label("Messages").classes("text-2xl font-bold mb-4").style(
            f'color: {THEME["accent"]};'
        )

        with ui.row().classes("w-full mb-2"):
            recipient = ui.input("Recipient Username").classes("w-full")
            group_id = ui.input("Group ID (optional)").classes("w-full")
            group_id.on("blur", lambda _: ui.run_async(refresh_messages()))
        content = ui.textarea("Message").classes("w-full mb-2")
        emoji_toolbar(content)

        async def send_message():
            data = {"content": content.value}
            if group_id.value:
                endpoint = f"/groups/{group_id.value}/messages"
            else:
                endpoint = f"/messages/{recipient.value}"
            resp = await api_call("POST", endpoint, data)
            if resp:
                ui.notify("Message sent!", color="positive")
                await refresh_messages()

        ui.button("Send", on_click=send_message).classes("w-full mb-4").style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        group_label = ui.label().classes("text-lg mb-2")
        messages_list = (
            ui.column()
            .classes("w-full")
            .style("max-height: 400px; overflow-y: auto")
        )

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
            if group_id.value:
                messages = await api_call(
                    "GET", f"/groups/{group_id.value}/messages"
                ) or []
                group = await api_call("GET", f"/groups/{group_id.value}") or {}
                group_label.text = group.get("name", f"Group {group_id.value}")
            else:
                messages = await api_call("GET", "/messages/") or []
                group_label.text = "Direct Messages"
            messages_list.clear()
            if not messages:
                ui.label("No messages yet. Start the conversation!").classes("text-sm")
                return
            for m in messages:
                with messages_list:
                    with (
                        ui.card()
                        .classes("w-full mb-2")
                        .style("border: 1px solid #333; background: #1e1e1e;")
                    ):
                        with ui.row().classes("items-center justify-between"):
                            with ui.column().classes("grow"):
                                ui.label(f"From: {m['sender_id']}").classes("text-sm")
                                ui.markdown(safe_markdown(m["content"])).classes("text-sm")
                            ui.button(
                                on_click=lambda msg=m: ui.run_async(open_edit(msg)),
                                icon="edit",
                            ).props("flat")

        await refresh_messages()
        ui.timer(30, lambda: ui.run_async(refresh_messages()))

        async def handle_event(event: dict) -> None:
            if event.get("type") == "message":
                await refresh_messages()

        ui.run_async(listen_ws(handle_event))
