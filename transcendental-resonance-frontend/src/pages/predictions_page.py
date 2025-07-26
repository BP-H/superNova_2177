"""Predictions dashboard page."""

from nicegui import ui

from utils.api import api_call, TOKEN, clear_token
from utils.styles import get_theme
from .login_page import login_page


@ui.page('/predictions')
async def predictions_page():
    """Display user and system level predictions."""
    if not TOKEN:
        ui.open(login_page)
        return

    user_data = api_call('GET', '/users/me')
    if not user_data:
        clear_token()
        ui.open(login_page)
        return

    user_id = user_data.get('id')
    user_pred = api_call('GET', f'/api/predict-user/{user_id}') or {}
    system_pred = api_call('GET', '/api/system-predictions') or {}

    THEME = get_theme()
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('Predictions').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        with ui.card().classes('w-full mb-4').style('border: 1px solid #333; background: #1e1e1e;'):
            ui.label('Your Predicted Interactions').classes('text-lg mb-2')
            if user_pred:
                preds = user_pred.get('prediction', {}).get('predictions', {})
                for action, info in preds.items():
                    prob = info.get('probability', 0.0)
                    ui.label(f'{action}: {prob:.2f}').classes('text-sm')
            else:
                ui.label('No data').classes('text-sm')

        with ui.card().classes('w-full').style('border: 1px solid #333; background: #1e1e1e;'):
            ui.label('System Predictions').classes('text-lg mb-2')
            if system_pred:
                experiments = system_pred.get('experiments', [])
                if experiments:
                    ui.label('Experiments:').classes('text-sm')
                    for exp in experiments:
                        ui.label(str(exp)).classes('text-sm break-words')
                prediction = system_pred.get('prediction')
                if prediction:
                    ui.label('Prediction:').classes('text-sm mt-2')
                    ui.label(str(prediction)).classes('text-sm break-words')
            else:
                ui.label('No data').classes('text-sm')
