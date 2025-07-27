.PHONY: install test lint

install:
python setup_env.py

test:
	pytest -q

lint:
	black --check .
	ruff .
	mypy
