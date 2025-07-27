"""Run a full introspection audit for a hypothesis."""

from __future__ import annotations

import asyncio
import json
import io
from nicegui import ui

from utils.styles import get_theme
from introspection.introspection_pipeline import run_full_audit
from db_models import SessionLocal


@ui.page('/introspection')
async def introspection_page():
    """Execute ``run_full_audit`` and show results."""
    THEME = get_theme()
    with ui.column().classes('w-full p-4').style(
        f'background: {THEME["gradient"]}; color: {THEME["text"]};'
    ):
        ui.label('Introspection Audit').classes('text-2xl font-bold mb-4').style(
            f'color: {THEME["accent"]};'
        )

        hyp_input = ui.input('Hypothesis ID').classes('w-full mb-2')
        run_btn = ui.button('Run Audit').classes('w-full mb-4').style(
            f'background: {THEME["primary"]}; color: {THEME["text"]};'
        )
        output_column = ui.column().classes('w-full')

        async def run_audit() -> None:
            output_column.clear()
            db = SessionLocal()
            try:
                bundle = await asyncio.to_thread(
                    run_full_audit, hyp_input.value, db
                )
            finally:
                db.close()

            if 'error' in bundle:
                ui.notify(bundle['error'], color='negative')
                return

            with output_column:
                with ui.expansion('Explanation', value=False):
                    ui.label(bundle.get('plain_text_report', '')).classes(
                        'whitespace-pre-wrap text-sm'
                    )
                with ui.expansion('Bias Summary', value=False):
                    ui.label(bundle.get('bias_summary', 'N/A')).classes(
                        'whitespace-pre-wrap text-sm'
                    )
                with ui.expansion('Causal Chain', value=False):
                    chain = bundle.get('causal_trace', [])
                    if chain:
                        for item in chain:
                            ui.label(str(item)).classes('text-sm')
                    else:
                        ui.label('No causal trace available').classes('text-sm')

                async def export() -> None:
                    data = json.dumps(bundle, indent=2)
                    ui.download(io.BytesIO(data.encode()), 'audit_bundle.json')

                ui.button('Export Bundle', on_click=export).classes('mt-4').style(
                    f'background: {THEME["accent"]}; color: {THEME["background"]};'
                )

        run_btn.on_click(run_audit)
