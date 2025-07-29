# fallback_ui.py

import streamlit as st
import os
import sys

# Optional: print to server logs
print("⚙️ Starting fallback UI...", file=sys.stderr)

# ✅ Always show something — avoid early exit
st.set_page_config(page_title="superNova Fallback", layout="wide")

st.title("🧪 superNova_2177 // Minimal Fallback UI")
st.markdown("If you're seeing this, the main app crashed or failed health check.")

# Optional diagnostics
if st.button("Show environment variables"):
    st.json(dict(os.environ))

# ✅ Optional: verify healthz manually
params = st.query_params
if "healthz" in params and "1" in params.get("healthz", []):
    st.success("✅ Health check passed!")
    st.stop()

st.info("You can replace this fallback_ui.py with your real UI once things are stable.")
