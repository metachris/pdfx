.DEFAULT_GOAL := help
.PHONY: deps help lint push test format check

deps:  ## Install dependencies
	pip install -e .
	pip install -r requirements_dev.txt

format:  ## Code formatting
	black pdfx

lint:  ## Linting (must pass)
	flake8 pdfx

check:  ## Lint and static-check
	pylint pdfx
	mypy pdfx

test:  ## Run tests
	pytest -ra

push:  ## Push code with tags
	git push && git push --tags

coverage:  ## Run tests with coverage
	coverage erase
	coverage run --include=pdfx/* -m pytest -ra
	coverage report -m
