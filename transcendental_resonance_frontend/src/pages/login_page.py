# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

"""Login and registration pages for Transcendental Resonance."""

from nicegui import ui

from utils.api import api_call, set_token
from utils.styles import get_theme


@ui.page("/")
async def login_page():
    """Render the login form and handle authentication."""
    THEME = get_theme()
    with (
        ui.column()
        .classes("w-full max-w-md mx-auto p-4")
        .style(f'background: {THEME["gradient"]}; color: {THEME["text"]};')
    ):
        ui.label("Transcendental Resonance").classes(
            "text-3xl font-bold text-center mb-4"
        ).style(f'color: {THEME["accent"]};')

        username = ui.input("Username").classes("w-full mb-2")
        password = ui.input("Password", password=True).classes("w-full mb-2")

        async def handle_login():
            data = {"username": username.value, "password": password.value}
            resp = await api_call("POST", "/token", data=data)
            if resp and "access_token" in resp:
                set_token(resp["access_token"])
                ui.notify("Login successful!", color="positive")
                from .profile_page import \
                    profile_page  # lazy import to avoid circular dependency

                ui.open(profile_page)
            else:
                ui.notify("Login failed", color="negative")

        ui.button("Login", on_click=handle_login).classes("w-full mb-4").style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )

        ui.label("New here? Register").classes("text-center cursor-pointer").on_click(
            lambda: ui.open(register_page)
        )

        ui.label(
            "This experimental social platform is not a financial product. "
            "All metrics are symbolic with no real-world value."
        ).classes("text-xs text-center opacity-70 mt-2")


@ui.page("/register")
async def register_page():
    """Render the registration form."""
    THEME = get_theme()
    with (
        ui.column()
        .classes("w-full max-w-md mx-auto p-4")
        .style(f'background: {THEME["gradient"]}; color: {THEME["text"]};')
    ):
        ui.label("Register").classes("text-2xl font-bold text-center mb-4").style(
            f'color: {THEME["accent"]};'
        )

        username = ui.input("Username").classes("w-full mb-2")
        email = ui.input("Email").classes("w-full mb-2")
        password = ui.input("Password", password=True).classes("w-full mb-2")

        async def handle_register():
            data = {
                "username": username.value,
                "email": email.value,
                "password": password.value,
            }
            resp = await api_call("POST", "/users/register", data)
            if resp:
                ui.notify("Registration successful! Please login.", color="positive")
                ui.open(login_page)
            else:
                ui.notify("Registration failed", color="negative")

        ui.button("Register", on_click=handle_register).classes("w-full mb-4").style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )
        ui.label("Back to Login").classes("text-center cursor-pointer").on_click(
            lambda: ui.open(login_page)
        )
