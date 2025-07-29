import streamlit as st
import os

# --- Health Check ---
# This check runs immediately to pass the Streamlit Cloud health probe.
if os.environ.get("PATH_INFO", "").rstrip("/") == "/healthz":
    st.write("ok")
    st.stop()

# --- Main App ---
st.set_page_config(page_title="✅ Sanity Check", layout="centered")

st.title("✅ It Works!")
st.success("The Streamlit environment is running and dependencies are stable.")
st.info("The crash is happening in your main application logic (`ui.py` or its imports).")

with st.expander("Next Steps"):
    st.markdown("""
        1.  **Confirm this page stays live.**
        2.  **Switch your main file back to `ui.py`.** The crash will likely return.
        3.  **Debug `ui.py`.** The error is now confirmed to be in that file or one of the modules it imports. Start by commenting out imports in `ui.py` to find the one that causes the crash.
    """)
