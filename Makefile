.PHONY: test setup clean run stop format lint

ROOT_DIR := .
GRADING_DIR ?= .grading
GRADE_FILE ?= $(GRADING_DIR)/grade.txt

# Default to skipping grade file generation
GENERATE_GRADE_FILE ?= false
PYTHON_CMD := uv run
PRECOMMIT_CMD := uvx pre-commit@4.1.0

# Default target
.DEFAULT_GOAL := help

# Help command
help:
	@echo "Lab Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make test         Run all tests"
	@echo "  make lint         Run all linters"
	@echo "  make clean        Clean cache files"
	@echo "  make setup        Setup development environment"


# Setup development environment
install-uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv venv

setup: clean 
	@echo "Setting up the environment."
	cd $(LAB_DIR) && \
	if ! command -v uv >/dev/null 2>&1; then \
		echo "uv not found, installing..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH="$$HOME/.cargo/bin:$$PATH"; \
	fi
	git clone https://github.com/srcolinas/teyuna.git
	uv add teyuna/packages/sdk-python
	uv add teyuna/packages/shared-core
	uv sync --dev

setup-validate:
	cd teyuna && make simulate

# Target to remove the score file before a fresh run
clean-score-file:
	@rm -f $(GRADE_FILE)
	@echo "Removed existing grade file if it existed."	

# Run all tests
test: clean-score-file
	@echo "Executing tests ..."
ifneq ($(GENERATE_GRADE_FILE),false)
	@echo "--- GRADING ENABLED: Creating grade file at $(GRADE_FILE) ---"
	@mkdir -p $(GRADING_DIR)
	
	@echo "Running all tests"
	@echo "TODO: Add your test commands here as in the example below."
	@$(MAKE) test-example
	cat $(GRADE_FILE)
else
	@echo "--- GRADING DISABLED: Skipping grade file creation. ---"
endif	
	@echo "Tests execution completed."

test-example:
	@echo "Running example test ..."
	# Example test command
	# ($(PYTHON_CMD) pytest tests/unit/test_example.py -vv) >> $(GRADE_FILE)


format:
	uv run ruff format src
	uv run ruff check --fix src

lint:
	uv run ruff format --check src
	uv run ruff check src
	uv run mypy

# Clean cache files
clean:
	@echo "Cleaning up the workspace"
	rm -rf teyuna/
	rm -rf .venv __pycache__ .mypy_cache .ruff_cache dist
	rm -rf src/**/__pycache__
	rm -rf src/**/.mypy_cache
	rm -rf src/**/.ruff_cache


BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 5173
export BACKEND_PORT FRONTEND_PORT
# Keep the frontend build's API URL aligned with the published backend port.
VITE_API_URL ?= http://localhost:$(BACKEND_PORT)
export VITE_API_URL


agent:=v1
run:
	cd teyuna && docker compose up -d
	@echo "Waiting for backend at http://127.0.0.1:$(BACKEND_PORT)/health ..."
	@until curl -sf "http://127.0.0.1:$(BACKEND_PORT)/health" >/dev/null; do sleep 1; done
	@echo "Backend:  http://127.0.0.1:$(BACKEND_PORT)"
	@echo "Frontend: http://127.0.0.1:$(FRONTEND_PORT)"
	@LOGDIR=logs/$$(date +%Y-%m-%d-%H-%M); \
	mkdir -p "$$LOGDIR"; \
	GAME_ID=$$(uv run teyuna-simulate create --host "http://127.0.0.1:$(BACKEND_PORT)"); \
	echo "Watch: http://127.0.0.1:$(FRONTEND_PORT)/?gameId=$$GAME_ID"; \
	echo "Logs:  $$LOGDIR"; \
	nohup uv run teyuna-simulate join "$$GAME_ID" --host "http://127.0.0.1:$(BACKEND_PORT)" --logdir "$$LOGDIR" \
		stochastic:alice stochastic:bob >"$$LOGDIR/simulate.out" 2>&1 & \
	echo $$! > logs/simulate.pid; \
	uv run python src/main.py --agent-version $(agent) --base-url "http://127.0.0.1:$(BACKEND_PORT)/" --game-id "$$GAME_ID"

stop:
	@if [ -f logs/simulate.pid ]; then \
		kill $$(cat logs/simulate.pid) 2>/dev/null || true; \
		rm -f logs/simulate.pid; \
	fi
	cd teyuna && docker compose down
