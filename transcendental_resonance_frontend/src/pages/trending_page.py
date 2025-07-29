"""Trending VibeNodes feed."""

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

from nicegui import ui

from utils.api import api_call, TOKEN
from utils.styles import get_theme
from utils.layout import page_container
from .login_page import login_page


@ui.page("/trending")
async def trending_page():
    """Display trending VibeNodes."""
    if not TOKEN:
        ui.open(login_page)
        return

    THEME = get_theme()
    with page_container(THEME):
        ui.label("Trending").classes("text-2xl font-bold mb-4").style(
            f'color: {THEME["accent"]};'
        )

        items = ui.column().classes("w-full")

        async def refresh_trending() -> None:
            data = await api_call("GET", "/vibenodes/trending") or []
            items.clear()
            for vn in data:
                with items:
                    with (
                        ui.card()
                        .classes("w-full mb-2")
                        .style("border: 1px solid #333; background: #1e1e1e;")
                    ):
                        ui.label(vn["name"]).classes("text-lg")
                        ui.label(vn["description"]).classes("text-sm")
                        if vn.get("media_url"):
                            mtype = vn.get("media_type", "")
                            if mtype.startswith("image"):
                                ui.image(vn["media_url"]).classes("w-full")
                            elif mtype.startswith("video"):
                                ui.video(vn["media_url"]).classes("w-full")
                            elif mtype.startswith("audio") or mtype.startswith("music"):
                                ui.audio(vn["media_url"]).classes("w-full")
                        ui.label(f"Likes: {vn.get('likes_count', 0)}").classes(
                            "text-sm"
                        )

                        async def like_fn(vn_id=vn["id"]):
                            await api_call("POST", f"/vibenodes/{vn_id}/like")
                            await refresh_trending()

                        ui.button("Like/Unlike", on_click=like_fn).style(
                            f'background: {THEME["accent"]}; color: {THEME["background"]};'
                        )

                        async def remix_fn(vn_id=vn["id"]):
                            await api_call("POST", f"/vibenodes/{vn_id}/remix")
                            ui.notify("Remix created!", color="positive")
                            await refresh_trending()

                        ui.button("Remix", on_click=remix_fn).style(
                            f'background: {THEME["primary"]}; color: {THEME["text"]};'
                        )

        await refresh_trending()
        ui.timer(60, lambda: ui.run_async(refresh_trending()))
