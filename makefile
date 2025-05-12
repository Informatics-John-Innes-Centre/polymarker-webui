init:
	flask --app pmwui init

run:
	flask --app pmwui run

debug:
	flask --app pmwui run --debug

test:
	pytest

coverage:
	coverage run -m pytest
	coverage report

check-deps:
	fawltydeps

build:
	python -m build --wheel
