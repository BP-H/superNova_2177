.PHONY: install test lint security

install:
	python setup_env.py

test:
	pytest -q

lint:
	mypy

security:
	bandit -r . -x tests || true
