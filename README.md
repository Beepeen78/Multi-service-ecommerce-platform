# Multi-Service E-Commerce Platform on Kubernetes

A production-ready, cloud-native e-commerce platform built with microservices architecture on Kubernetes.

## Architecture Overview

> 📊 **Detailed Architecture**: See [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md) for diagrams and detailed request flow.

### Request Flow: User → Gateway → Service → Database → Events

**Example: Order Processing Flow**
```
1. User Request 
   ↓
2. Ingress-NGINX (TLS termination, routing)
   ↓
3. Istio Service Mesh (traffic management, canary routing)
   ↓
4. Order Service (business logic)
   ├─→ PostgreSQL (persist order data)
   ├─→ Redis (cache order status)
   └─→ Kafka (publish order.created event)
       ↓
5. Notification Service (Kafka consumer)
   ├─→ PostgreSQL (store notification)
   └─→ Redis (cache notification)
       ↓
6. User receives notification
```

**Complete Request Journey**: User → Gateway → Service → Database → Events → Notification Service → User

### Microservices (9 Services) - Tech Stack & Purpose

| Service | Language | Framework | Database | Cache | Purpose |
|---------|----------|-----------|----------|-------|---------|
| **auth-service** | Node.js | Express.js | PostgreSQL | Redis | Authentication, JWT token management, user registration/login |
| **user-service** | Go | Standard library | PostgreSQL | Redis | User profile management, user data retrieval |
| **product-service** | Node.js | Express.js | PostgreSQL | Redis | Product catalog, search, filtering, category browsing |
| **inventory-service** | Python | Flask | PostgreSQL | Redis | Inventory management, stock reservation/release |
| **cart-service** | Node.js | Express.js | - | Redis | Shopping cart management, session-based storage |
| **order-service** | Go | Standard library | PostgreSQL | Redis | Order creation, Kafka event publishing, KEDA autoscaling |
| **payment-service** | Node.js | Express.js | PostgreSQL | Redis | Payment processing, transaction management |
| **notification-service** | Python | Flask | PostgreSQL | Redis | Email/SMS notifications, Kafka consumer |
| **recommendation-service** | Python | Flask | PostgreSQL | Redis | Product recommendations, ML-based suggestions |

### Technology Stack

- **Languages**: Node.js (Express), Go (standard library), Python (Flask)
- **Communication**: REST (external APIs), Kafka (event-driven async)
- **Databases**: PostgreSQL (primary, ACID transactions), Redis (caching, sessions)
- **Message Queue**: Kafka (event streaming, async communication)
- **Service Mesh**: Istio (traffic management, canary deployments, mTLS)
- **Container Orchestration**: Kubernetes (Helm, HPA, KEDA)

### Kubernetes Features
- ✅ Helm charts for entire application
- ✅ Ingress-NGINX with TLS (Let's Encrypt)
- ✅ Horizontal Pod Autoscaler (HPA)
- ✅ Prometheus + Grafana monitoring
- ✅ Loki + Promtail for centralized logging
- ✅ KEDA for event-driven autoscaling
- ✅ CI/CD with GitHub Actions → ArgoCD (GitOps)
- ✅ Canary deployments with Istio

## Project Structure

```
.
├── services/              # Microservices source code
│   ├── auth-service/
│   ├── user-service/
│   ├── product-service/
│   ├── inventory-service/
│   ├── cart-service/
│   ├── order-service/
│   ├── payment-service/
│   ├── notification-service/
│   └── recommendation-service/
├── helm/                  # Helm charts
│   ├── ecommerce-platform/
│   └── infrastructure/
├── k8s/                   # Kubernetes manifests
│   ├── base/
│   └── overlays/
├── .github/               # GitHub Actions workflows
│   └── workflows/
├── argocd/                # ArgoCD configurations
├── monitoring/            # Prometheus & Grafana configs
├── logging/               # Loki & Promtail configs
└── istio/                 # Istio service mesh configs
```

## Quick Start

### Prerequisites
- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3.x
- Docker
- Istio 1.17+

### Installation

1. **Install Infrastructure Components**
```bash
# Install Ingress-NGINX
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx

# Install Cert-Manager for TLS
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager --set installCRDs=true

# Install Prometheus Stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Install Loki Stack
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack

# Install KEDA
helm repo add kedacore https://kedacore.github.io/charts
helm install keda kedacore/keda

# Install Istio
istioctl install --set values.defaultRevision=default
```

2. **Deploy Application with Helm**
```bash
cd helm/ecommerce-platform
helm install ecommerce . --namespace ecommerce --create-namespace
```

3. **Deploy with ArgoCD (GitOps)**
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Create ArgoCD application
kubectl apply -f argocd/applications/ecommerce-platform.yaml
```

## Development

### Building Services
```bash
# Build all services
make build

# Build specific service
make build SERVICE=auth-service
```

### Running Locally
```bash
# Start infrastructure (PostgreSQL, Redis, Kafka)
docker-compose up -d

# Run services locally
make run SERVICE=auth-service
```

### Testing

### Quick Test
```bash
# Start services
docker-compose up -d

# Run API test suite (Linux/Mac)
./tests/api/test-ecommerce-flow.sh

# Or on Windows
bash tests/api/test-ecommerce-flow.sh
```

### Unit Tests
```bash
# Run all tests
make test

# Run tests for specific service
make test SERVICE=auth-service
```

### Comprehensive Testing
See [TESTING.md](TESTING.md) for detailed testing guide including:
- Unit tests
- Integration tests
- API testing
- Load testing
- Kubernetes testing
- E2E testing

## Monitoring & Observability

- **Grafana Dashboard**: http://grafana.ecommerce.local
- **Prometheus**: http://prometheus.ecommerce.local
- **Loki Logs**: http://loki.ecommerce.local

## CI/CD Pipeline

The CI/CD pipeline is configured with:
- **GitHub Actions**: Builds, tests, and pushes Docker images
- **ArgoCD**: Automatically syncs changes from Git to Kubernetes

## Service Communication

- **External APIs**: REST over HTTPS
- **Internal Services**: gRPC
- **Event-Driven**: Kafka topics

## Scaling

- **HPA**: CPU/Memory based scaling
- **KEDA**: Event-driven scaling (Kafka lag, queue depth)

## Canary Deployments

Canary deployments are configured using Istio VirtualServices and DestinationRules. See `istio/canary/` for examples.

## Documentation

- [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md) - **Architecture diagrams and request flow**
- [Deployment Guide](DEPLOYMENT.md) - Detailed deployment instructions
- [Architecture Documentation](ARCHITECTURE.md) - System architecture and design
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines
- [Testing Guide](TESTING.md) - Comprehensive testing documentation

## Project Structure

```
.
├── services/              # Microservices source code
│   ├── auth-service/     # Node.js - Authentication
│   ├── user-service/     # Go - User management
│   ├── product-service/  # Node.js - Product catalog
│   ├── inventory-service/# Python - Inventory management
│   ├── cart-service/     # Node.js - Shopping cart
│   ├── order-service/    # Go - Order processing
│   ├── payment-service/  # Node.js - Payment processing
│   ├── notification-service/ # Python - Notifications
│   └── recommendation-service/ # Python - Recommendations
├── helm/                 # Helm charts
│   └── ecommerce-platform/
├── k8s/                  # Kubernetes manifests
│   ├── cert-manager/     # TLS certificates
│   └── database/         # Database initialization
├── monitoring/           # Prometheus & Grafana configs
├── logging/              # Loki & Promtail configs
├── .github/              # GitHub Actions workflows
├── argocd/               # ArgoCD configurations
└── istio/                # Istio service mesh configs
```

## Features

### ✅ Implemented
- 9 microservices (Node.js, Go, Python)
- Helm charts for entire platform
- Ingress-NGINX with TLS
- HPA for all services
- Prometheus + Grafana monitoring
- Loki + Promtail logging
- KEDA for event-driven autoscaling
- GitHub Actions CI/CD
- ArgoCD GitOps
- Istio canary deployments
- PostgreSQL + Redis + Kafka
- Docker Compose for local development

### 🚀 Future Enhancements
- gRPC inter-service communication
- Distributed tracing with Jaeger
- Advanced ML recommendations
- Multi-region deployment
- Service mesh observability
- Advanced security policies

## What I Learned / Key Responsibilities

### Microservices Architecture & Design
- Designed and implemented 9 microservices using Node.js, Go, and Python
- Implemented service-to-service communication patterns (REST, event-driven)
- Designed database schema and data flow across distributed services
- Implemented caching strategies (Redis) and session management
- Built event-driven architecture with Kafka for async processing

### Container Orchestration & Kubernetes
- Created comprehensive Helm charts for entire application stack
- Configured Horizontal Pod Autoscaler (HPA) for CPU/memory-based scaling
- Implemented KEDA for event-driven autoscaling based on Kafka lag
- Set up Ingress-NGINX with TLS termination using Let's Encrypt
- Configured Istio service mesh for traffic management and canary deployments

### Observability & Monitoring
- Integrated Prometheus for metrics collection across all services
- Set up Grafana dashboards for visualization and alerting
- Implemented centralized logging with Loki and Promtail
- Added health check endpoints and service monitoring
- Configured ServiceMonitor for automatic metrics discovery

### CI/CD & GitOps
- Built GitHub Actions pipeline for automated builds and tests
- Implemented ArgoCD for GitOps-based deployments
- Created multi-stage Docker builds for optimized images
- Set up automated testing (unit, integration, E2E)

### Infrastructure as Code
- Wrote Kubernetes manifests and Helm templates
- Configured cert-manager for automated TLS certificate management
- Set up infrastructure components (PostgreSQL, Redis, Kafka) via Helm
- Created comprehensive documentation and deployment guides

### Best Practices
- Implemented health checks, readiness probes, and liveness probes
- Added resource limits and requests for all services
- Designed for high availability with multi-replica deployments
- Created comprehensive testing suite (unit, integration, load, E2E)
- Documented architecture, deployment, and contribution guidelines

## License

MIT

