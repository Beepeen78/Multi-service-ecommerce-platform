# Quick Start Guide

Get the e-commerce platform running in 5 minutes!

## Prerequisites Check

```bash
# Check Kubernetes
kubectl version --client

# Check Helm
helm version

# Check Docker
docker --version
```

## Option 1: Local Development (Docker Compose)

```bash
# Start infrastructure
docker-compose up -d

# Wait for services to be ready
sleep 30

# Test a service
curl http://localhost:3001/health
```

## Option 2: Kubernetes (Minikube)

```bash
# Start Minikube
minikube start

# Enable ingress
minikube addons enable ingress

# Install infrastructure (see DEPLOYMENT.md for details)
# Then deploy:
cd helm/ecommerce-platform
helm dependency update
helm install ecommerce . --namespace ecommerce --create-namespace
```

## Option 3: Full Production Setup

Follow the [Deployment Guide](DEPLOYMENT.md) for complete production setup with:
- TLS certificates
- Monitoring
- Logging
- CI/CD
- Service mesh

## Test the API

```bash
# Register a user
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","name":"Test User"}'

# Login
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get products
curl http://localhost:3003/api/products
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

