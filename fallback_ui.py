import streamlit as st

st.set_page_config(page_title="superNova_2177 fallback", layout="centered")
st.title("🧪 Fallback UI")

st.success("✅ Streamlit works — your environment is fine.")
st.info("The crash is happening inside your main UI script.")

with st.expander("Troubleshooting tips"):
    st.markdown("""
    - Try running only `render_main_ui()` in isolation
    - Import your pages one by one and watch for errors
    - Check for large/broken imports (`torch`, `qutip`, etc.)
    - If using Streamlit Cloud: double-check files and subdirs exist
    """)
