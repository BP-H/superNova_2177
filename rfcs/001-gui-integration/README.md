# Streamlit GUI Integration

## Problem Statement
The validation toolkit currently requires command-line interaction, which can be a barrier for non-technical users who want to run or review validations.

## Proposed Solution
Introduce a `ui.py` module built with Streamlit that exposes the existing `validate_hypothesis` logic through a simple web interface. Users can select a hypothesis file, trigger validation, and view the resulting reports directly in the browser.

## Alternatives
- Continue relying solely on the command-line interface.
- Build a custom React or Django front‑end instead of Streamlit.

## Impact
A lightweight GUI makes the validation pipeline more accessible and provides a starting point for future web-based features. Deployment can be as easy as running `streamlit run ui.py` on a server or container.
