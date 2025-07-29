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

The Streamlit app also supports a lightweight health check for CI or uptime
monitors. Visiting `/?healthz=1` responds with `ok` and stops execution. This
serves as a simple fallback when the built-in `/healthz` route isn't available,
so monitoring systems can confirm the UI started successfully.
