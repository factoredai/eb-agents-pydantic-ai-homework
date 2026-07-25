.PHONY: test coverage install dev setup clean lint check help

UV := uv
SRC_DIR := src
TEST_DIR := tests

.DEFAULT_GOAL := help

help:
	@echo "Vocareum Plugin Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make setup        Setup development environment"
	@echo "  make install      Install project dependencies"
	@echo "  make dev          Install development dependencies"
	@echo "  make test         Run all tests"
	@echo "  make coverage     Run tests with coverage report"
	@echo "  make lint         Run linters and static analysis"
	@echo "  make clean        Clean cache files"

setup: clean
	@echo "Setting up the environment"
	$(UV) venv

dev:
	@echo "Installing dependencies..."
	$(UV) pip install --system -e ".[dev]"
	$(UV) pip install pytest-cov
	$(UV) sync --all-extras

test:
	@echo "Executing tests..."
	$(UV) run pytest $(TEST_DIR) --cov=$(SRC_DIR)/vocareum_plugin --cov-report=term

coverage:
	@echo "Generating coverage report..."
	$(UV) run pytest $(TEST_DIR) --cov=$(SRC_DIR)/vocareum_plugin --cov-report=html
	@echo "📄 Open htmlcov/index.html to view the coverage report"

lint:
	@echo "Running linters..."
	$(UV) run ruff format .
	$(UV) run ruff check . --fix
	$(UV) run mypy $(SRC_DIR) --check-untyped-defs

check: lint test

clean:
	@echo "Cleaning up the workspace"
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
