STRICTLY A SOCIAL MEDIA PLATFORM
Intellectual Property & Artistic Inspiration
Legal & Ethical Safeguards

# Extending the Streamlit UI

`streamlit_helpers.py` exposes small utilities used by `ui.py` for common tasks.
Import these helpers in your own modules to keep layouts consistent.

```python
import streamlit as st
from streamlit_helpers import header, theme_selector, centered_container

header("Custom Page", layout="wide")
with centered_container():
    theme_selector("Theme")
    st.write("Hello World")
```

Running this example will render a page with the standard header, a theme switcher
radio button and a centered content area.
