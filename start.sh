#!/bin/bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

# Launch the NiceGUI wrapper for Streamlit Cloud
UI_FILE="transcendental_resonance_frontend/ui.py"

if [[ ! -f "$UI_FILE" ]]; then
  echo "❌ $UI_FILE not found. Please ensure it exists." >&2
  exit 1
fi

PORT="${STREAMLIT_PORT:-${PORT:-8888}}"

echo "🚀 Launching Streamlit UI: $UI_FILE on port $PORT"
streamlit run "$UI_FILE" \
  --server.headless true \
  --server.address 0.0.0.0 \
  --server.port "$PORT"
