.PHONY: help install install-dev install-all test test-unit test-integration test-cov web clean lint migrate cleanup uv-install uv-sync uv-run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===== UV Commands (Recommended) =====
uv-install: ## Install project with uv (creates virtual env)
	uv venv
	uv pip install -e ".[dev,llm,scheduler]"

uv-sync: ## Sync dependencies with uv
	uv pip install -e ".[dev,llm,scheduler]"

uv-run: ## Run application with uv
	uv run python main.py

uv-test: ## Run tests with uv
	uv run pytest tests/ -v

# ===== Traditional pip Commands =====
install: ## Install base dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

install-all: ## Install all dependencies (including LLM SDKs)
	pip install -e ".[dev,llm,scheduler]"

# ===== Testing =====
test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=internal --cov-report=html --cov-report=term

# ===== Application =====
web: ## Start the web server
	python main.py

# ===== Maintenance =====
clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	rm -rf .pytest_cache htmlcov/ .coverage

lint: ## Run code linting
	pylint internal/

migrate: ## Run database migrations
	python3 scripts/migrate.py

cleanup: ## Run audio cleanup job
	python3 -c "from internal.services.audio_cleaner import cleanup_job; cleanup_job()"
