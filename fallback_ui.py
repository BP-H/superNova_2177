import streamlit as st
import sys
import os

# 1. ⚕️ Minimal early health check
def check_health():
    try:
        params = st.query_params
        if "1" in params.get("healthz", []):
            st.write("ok")
            st.stop()
    except Exception as e:
        print(f"[healthz check failed] {e}", file=sys.stderr)

check_health()

# 2. ✅ Confirmed Streamlit is working
st.set_page_config(page_title="superNova_2177", layout="wide")
st.markdown("# 🚀 superNova_2177 UI Loaded")
st.info("✅ Streamlit started successfully. No crash in top-level script.")

# 3. 🧪 Try minimal import inside safe block
try:
    from ui_utils import render_main_ui
    render_main_ui()
except Exception as e:
    st.warning("Optional UI module failed to load.")
    st.code(str(e))
