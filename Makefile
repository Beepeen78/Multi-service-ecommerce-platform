.PHONY: help build up down logs restart clean deploy-dev deploy-prod deploy-k8s test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker-compose build

up: ## Start all services (production)
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

restart: ## Restart all services
	docker-compose restart

clean: ## Remove containers, networks, and volumes
	docker-compose down -v
	docker system prune -f

# Development targets
dev-build: ## Build development images
	docker-compose -f docker-compose.dev.yml build

dev-up: ## Start all services (development)
	docker-compose -f docker-compose.dev.yml up -d

dev-down: ## Stop development services
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## View development logs
	docker-compose -f docker-compose.dev.yml logs -f

# Deployment targets
deploy-dev: ## Deploy to development environment
	@echo "Deploying to development..."
	docker-compose -f docker-compose.dev.yml down
	docker-compose -f docker-compose.dev.yml build
	docker-compose -f docker-compose.dev.yml up -d

deploy-prod: ## Deploy to production environment
	@echo "Deploying to production..."
	docker-compose down
	docker-compose build
	docker-compose up -d

deploy-k8s: ## Deploy to Kubernetes
	@echo "Deploying to Kubernetes..."
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secrets.yaml
	kubectl apply -f k8s/postgres-deployment.yaml
	kubectl apply -f k8s/redis-deployment.yaml
	kubectl apply -f k8s/api-gateway-deployment.yaml

# Testing targets
test: ## Run tests (requires services to be implemented)
	@echo "Running tests..."
	@echo "Add your test commands here"

# Utility targets
ps: ## Show running containers
	docker-compose ps

status: ## Show service status
	@echo "=== Docker Compose Services ==="
	docker-compose ps
	@echo ""
	@echo "=== Kubernetes Services ==="
	kubectl get pods -n ecommerce-platform 2>/dev/null || echo "Kubernetes not configured"

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8080/health || echo "API Gateway not responding"

shell-api-gateway: ## Open shell in API Gateway container
	docker-compose exec api-gateway sh

shell-postgres: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U user -d ecommerce

shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli

