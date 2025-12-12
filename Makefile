.PHONY: help build test run deploy clean

SERVICE ?= all
REGISTRY ?= localhost:5000
VERSION ?= latest

help:
	@echo "Available targets:"
	@echo "  build       - Build Docker images for services"
	@echo "  test        - Run tests"
	@echo "  run         - Run service locally"
	@echo "  deploy      - Deploy to Kubernetes"
	@echo "  clean       - Clean build artifacts"

build:
	@if [ "$(SERVICE)" = "all" ]; then \
		for service in services/*/; do \
			service_name=$$(basename $$service); \
			echo "Building $$service_name..."; \
			docker build -t $(REGISTRY)/$$service_name:$(VERSION) -f $$service/Dockerfile $$service; \
		done; \
	else \
		echo "Building $(SERVICE)..."; \
		docker build -t $(REGISTRY)/$(SERVICE):$(VERSION) -f services/$(SERVICE)/Dockerfile services/$(SERVICE); \
	fi

test:
	@if [ "$(SERVICE)" = "all" ]; then \
		for service in services/*/; do \
			service_name=$$(basename $$service); \
			echo "Testing $$service_name..."; \
			cd $$service && npm test || go test ./... || pytest || true; \
			cd ../..; \
		done; \
	else \
		cd services/$(SERVICE) && npm test || go test ./... || pytest; \
	fi

run:
	@if [ "$(SERVICE)" = "all" ]; then \
		echo "Use docker-compose to run all services"; \
	else \
		cd services/$(SERVICE) && npm start || go run . || python app.py; \
	fi

deploy:
	@echo "Deploying with Helm..."
	cd helm/ecommerce-platform && helm upgrade --install ecommerce . --namespace ecommerce --create-namespace

clean:
	@echo "Cleaning build artifacts..."
	docker system prune -f
	rm -rf dist/ build/

