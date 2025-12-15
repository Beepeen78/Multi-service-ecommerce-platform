# PowerShell deployment script for Multi-Service E-Commerce Platform

param(
    [string]$Environment = "production",
    [string]$Method = "docker",
    [string]$Registry = "your-registry",
    [string]$Namespace = "ecommerce-platform"
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "Starting deployment for environment: $Environment"

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-ColorOutput Red "Error: Docker is not running"
    exit 1
}

# Function to deploy with Docker Compose
function Deploy-DockerCompose {
    Write-ColorOutput Yellow "Deploying with Docker Compose..."
    
    if ($Environment -eq "development") {
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml build
        docker-compose -f docker-compose.dev.yml up -d
    } else {
        docker-compose down
        docker-compose build
        docker-compose up -d
    }
    
    Write-ColorOutput Green "Docker Compose deployment completed"
}

# Function to deploy with Kubernetes
function Deploy-Kubernetes {
    Write-ColorOutput Yellow "Deploying with Kubernetes..."
    
    # Check if kubectl is installed
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-ColorOutput Red "Error: kubectl is not installed"
        exit 1
    }
    
    # Apply namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply ConfigMap and Secrets
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    
    # Deploy databases first
    kubectl apply -f k8s/postgres-deployment.yaml
    kubectl apply -f k8s/redis-deployment.yaml
    
    # Wait for databases to be ready
    Write-ColorOutput Yellow "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n $Namespace --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n $Namespace --timeout=300s
    
    # Deploy services
    kubectl apply -f k8s/api-gateway-deployment.yaml
    
    Write-ColorOutput Green "Kubernetes deployment completed"
}

# Main deployment logic
switch ($Method.ToLower()) {
    "docker" {
        Deploy-DockerCompose
    }
    "k8s" {
        Deploy-Kubernetes
    }
    "kubernetes" {
        Deploy-Kubernetes
    }
    default {
        Write-ColorOutput Yellow "Deployment method not specified. Using Docker Compose..."
        Deploy-DockerCompose
    }
}

Write-ColorOutput Green "Deployment completed successfully!"

