#!/bin/bash

if ! command -v streamlit >/dev/null; then
    echo "Streamlit is not installed. Run 'pip install -r requirements.txt' first." >&2
    exit 1
fi

streamlit run ui.py
