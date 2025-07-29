#!/usr/bin/env bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
PORT="${STREAMLIT_PORT:-8888}"
exec streamlit run streamlit_app.py --server.port "$PORT"
