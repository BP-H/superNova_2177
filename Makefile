.PHONY: install test lint

install:
	./setup.sh

test:
	pytest -q

lint:
	mypy
