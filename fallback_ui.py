import streamlit as st

st.set_page_config(page_title="✅ Sanity Check", layout="centered")

st.title("🧠 streamlit is alive!")
st.write("If you're seeing this, your environment is working.")

# 👇 this forces streamlit to keep running
if st.button("Click me to stay awake"):
    st.success("yep, we're alive.")
