.PHONY: help install dev-install run test lint format clean docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make run           - Run development server"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean cache and build files"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migration     - Create new migration"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black ruff mypy pre-commit
	pre-commit install

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v --cov=app --cov-report=term-missing --cov-report=html

lint:
	ruff check app tests
	mypy app

format:
	black app tests
	ruff check --fix app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov
	rm -rf .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

migrate:
	alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

downgrade:
	alembic downgrade -1

db-shell:
	docker-compose exec db psql -U postgres -d fastapi_db

redis-cli:
	docker-compose exec redis redis-cli
