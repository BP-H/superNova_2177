.PHONY: install test lint

install:
        ./setup_env.sh

test:
	pytest -q

lint:
	mypy
