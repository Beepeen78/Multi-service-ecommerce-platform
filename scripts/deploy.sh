#!/bin/bash

# Deployment script for Multi-Service E-Commerce Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
REGISTRY=${REGISTRY:-"your-registry"}
NAMESPACE=${NAMESPACE:-"ecommerce-platform"}

echo -e "${GREEN}Starting deployment for environment: ${ENVIRONMENT}${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Function to deploy with Docker Compose
deploy_docker_compose() {
    echo -e "${YELLOW}Deploying with Docker Compose...${NC}"
    
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml build
        docker-compose -f docker-compose.dev.yml up -d
    else
        docker-compose down
        docker-compose build
        docker-compose up -d
    fi
    
    echo -e "${GREEN}Docker Compose deployment completed${NC}"
}

# Function to deploy with Kubernetes
deploy_kubernetes() {
    echo -e "${YELLOW}Deploying with Kubernetes...${NC}"
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl is not installed${NC}"
        exit 1
    fi
    
    # Apply namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply ConfigMap and Secrets
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    
    # Deploy databases first
    kubectl apply -f k8s/postgres-deployment.yaml
    kubectl apply -f k8s/redis-deployment.yaml
    
    # Wait for databases to be ready
    echo -e "${YELLOW}Waiting for databases to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    
    # Deploy services
    kubectl apply -f k8s/api-gateway-deployment.yaml
    # Add other service deployments here
    
    echo -e "${GREEN}Kubernetes deployment completed${NC}"
}

# Main deployment logic
case "$2" in
    docker)
        deploy_docker_compose
        ;;
    k8s|kubernetes)
        deploy_kubernetes
        ;;
    *)
        echo -e "${YELLOW}Deployment method not specified. Using Docker Compose...${NC}"
        deploy_docker_compose
        ;;
esac

echo -e "${GREEN}Deployment completed successfully!${NC}"

