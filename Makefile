.PHONY: dev test lint

dev:
	docker compose up --build

test:
	poetry run pytest

lint:
	poetry run python -m compileall src tests
