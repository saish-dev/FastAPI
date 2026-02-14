.PHONY: help up down logs clean test generate-grpc

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services
	docker compose up --build

down: ## Stop all services
	docker compose down

logs: ## View logs from all services
	docker compose logs -f

clean: ## Clean up containers and volumes
	docker compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test: ## Run tests for all services
	cd auth-service && pytest
	cd user-service && pytest
	cd gateway-service && pytest

generate-grpc: ## Generate gRPC code from proto files
	./generate_grpc.sh

auth-logs: ## View auth-service logs
	docker compose logs -f auth-service

user-logs: ## View user-service logs
	docker compose logs -f user-service

gateway-logs: ## View gateway-service logs
	docker compose logs -f gateway-service

nats-logs: ## View NATS logs
	docker compose logs -f nats

db-auth: ## Connect to auth database
	docker compose exec auth-db psql -U postgres -d auth_db

db-user: ## Connect to user database
	docker compose exec user-db psql -U postgres -d user_db

restart: ## Restart all services
	docker compose restart

rebuild: ## Rebuild and restart all services
	docker compose up --build -d
