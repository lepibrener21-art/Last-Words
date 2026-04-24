.PHONY: help install test test-unit test-integration lint format typecheck play clean

help:
	@echo "Last Words — common tasks"
	@echo ""
	@echo "  make install          Install the package with dev + anthropic extras."
	@echo "  make test             Run unit tests."
	@echo "  make test-unit        Run unit tests (alias for 'test')."
	@echo "  make test-integration Run integration tests (requires ANTHROPIC_API_KEY)."
	@echo "  make lint             Run ruff linter."
	@echo "  make format           Run ruff formatter."
	@echo "  make typecheck        Run mypy."
	@echo "  make play             Play the game (requires ANTHROPIC_API_KEY)."
	@echo "  make clean            Remove build artifacts and caches."

install:
	pip install -e ".[anthropic,dev]"

test: test-unit

test-unit:
	pytest tests/unit -v

test-integration:
	@if [ -z "$$ANTHROPIC_API_KEY" ]; then \
		echo "ERROR: ANTHROPIC_API_KEY is not set."; \
		exit 1; \
	fi
	pytest tests/integration -m integration -v

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

typecheck:
	mypy src/last_words/

play:
	@if [ -z "$$ANTHROPIC_API_KEY" ]; then \
		echo "ERROR: ANTHROPIC_API_KEY is not set."; \
		exit 1; \
	fi
	last-words play

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
