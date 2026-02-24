dev:
	docker compose -f dev-compose.yaml --env-file .env.example up -d --build

down:
	docker compose -f dev-compose.yaml down

init:
	docker compose -f dev-compose.yaml exec polymarker uv run --no-sync flask --app pmwui init

import-genome:
	docker compose -f dev-compose.yaml exec polymarker uv run --no-sync flask --app pmwui import $(FILE)

test:
	pytest

coverage:
	coverage run -m pytest
	coverage report

check-deps:
	fawltydeps

build:
	uv run python -m build --wheel
