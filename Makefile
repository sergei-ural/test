dev:
	docker compose up --build

env:
	cp .env.example .env

test:
	poetry run pytest

lint:
	poetry run ruff check src tests
