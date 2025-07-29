from nicegui import ui


def render_media_block(url: str | None, mtype: str | None) -> None:
    """Render media based on type with graceful fallback."""
    if not url or not mtype:
        ui.html("<p>No media</p>")
        return
    mtype = mtype.lower()
    if mtype.startswith("image"):
        ui.image(url).classes("w-full")
    elif mtype.startswith("video"):
        ui.label("\U0001F3A5").classes("text-lg")
        ui.video(url).classes("w-full")
    elif mtype.startswith("audio") or mtype.startswith("music"):
        ui.label("\U0001F3A4").classes("text-lg")
        ui.audio(url).classes("w-full")
    else:
        ui.html("<p>No media</p>")
