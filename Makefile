.PHONY: install test lint ui

install:
	python setup_env.py

test:
	pytest -q

lint:
	mypy

ui:
        streamlit run ui.py
