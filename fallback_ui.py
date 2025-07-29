import streamlit as st

st.set_page_config(page_title="debug / fallback", layout="centered")
st.title("🧪 superNova_2177 fallback UI")

st.success("✅ Streamlit is running! This means the crash is in your main UI code.")
st.info("Try commenting out `main()` in your real `ui.py` or disable auto-loading pages.")

with st.expander("Next Steps"):
    st.markdown("""
    - Check which `render_*` function crashes
    - Try importing each page module manually
    - Run `ui.py` line-by-line until you isolate the crash
    - Then gradually re-enable modules one-by-one
    """)
