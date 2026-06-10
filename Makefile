.PHONY: setup run test lint lint-fix clean build

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

run:
	$(PYTHON) -m src.main

test:
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check src/ tests/

lint-fix:
	$(PYTHON) -m ruff check src/ tests/ --fix

clean:
	rm -rf dist/ build/ *.spec .pytest_cache .ruff_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build:
	$(PIP) install pyinstaller
	bash build/build_macos.sh
