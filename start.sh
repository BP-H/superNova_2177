#!/bin/bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

# Dynamically find ui.py and launch it
UI_FILE=$(find . -type f -name "ui.py" | head -n 1)

if [[ -z "$UI_FILE" ]]; then
  echo "❌ ui.py not found. Please ensure it exists." >&2
  exit 1
fi

echo "🚀 Launching Streamlit UI: $UI_FILE"
PORT="${STREAMLIT_PORT:-${PORT:-8888}}"
streamlit run "$UI_FILE" \
  --server.headless true \
  --server.address 0.0.0.0 \
  --server.port "$PORT"
