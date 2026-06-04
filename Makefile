.PHONY: help

# Default target
help:
	@echo "LaRencontre Website - Commands"
	@echo ""
	@echo "=== Backend (LRWebsiteBackend) ==="
	@echo "  make install    Install backend dependencies"
	@echo "  make dev        Start backend dev server (port 8000)"
	@echo "  make test       Run backend tests"
	@echo "  make test-v     Run backend tests with verbose output"
	@echo ""

# === Backend ===
install:
	poetry install

dev:
	poetry run uvicorn app.main:app --reload

test:
	poetry run pytest tests/

test-v:
	poetry run pytest tests/ -v
