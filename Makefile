.PHONY: help install install-cli install-ha install-dev test test-unit test-integration test-cov lint format type-check clean validate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install base dependencies
	uv pip install -e .

install-cli: ## Install CLI dependencies
	uv pip install -e ".[cli]"

install-ha: ## Install Home Assistant dependencies
	uv pip install -e ".[ha]"

install-dev: ## Install dev dependencies
	uv pip install -e ".[dev,cli,ha]"

test: ## Run all tests (unit only, no integration)
	uv run pytest -m "not integration"

test-unit: ## Run unit tests only
	uv run pytest tests/test_client.py tests/test_models.py tests/test_ha_coordinator.py tests/test_ha_config_flow.py -v

test-integration: ## Run integration tests (requires device)
	@echo "Running integration tests - requires NETCOMMANDER_HOST and RUN_INTEGRATION_TESTS=1"
	RUN_INTEGRATION_TESTS=1 uv run pytest tests/test_integration.py -v -s

test-cov: ## Run tests with coverage report
	uv run pytest -m "not integration" --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint: ## Run linting
	uv run ruff check src/netcommander custom_components/netcommander netcommander_cli tests

format: ## Format code
	uv run black src/netcommander custom_components/netcommander netcommander_cli tests
	uv run ruff check --fix src/netcommander custom_components/netcommander netcommander_cli tests

type-check: ## Run type checking
	uv run mypy src/netcommander custom_components/netcommander

clean: ## Clean build artifacts
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov .pytest_cache .mypy_cache .ruff_cache

.DEFAULT_GOAL := help
