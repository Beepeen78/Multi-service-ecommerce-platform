# 🛍️ Multi-Service E-Commerce Platform

> **A production-ready microservices-based e-commerce platform built with Python/FastAPI, containerized with Docker, and orchestrated with Kubernetes.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5.svg)](https://kubernetes.io/)
[![License](https://img.shields.io/badge/License-ISC-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Strengths](#-strengths)
- [Weaknesses & Future Improvements](#-weaknesses--future-improvements)
- [Presentation Points](#-presentation-points)
- [Contributing](#-contributing)

---

## 🎯 Overview

This project demonstrates a **production-grade microservices architecture** for an e-commerce platform. The system is designed with scalability, maintainability, and separation of concerns as core principles.

### Key Highlights

- **Microservices Architecture**: 5+ independent services, each handling a specific business domain
- **Python/FastAPI**: Modern, high-performance async framework with automatic API documentation
- **Containerization**: Fully containerized with Docker for consistent deployments
- **Orchestration**: Kubernetes manifests for production deployment
- **CI/CD**: Automated builds and deployments via GitHub Actions
- **Cloud-Native**: Designed for horizontal scaling and high availability

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│              (Web Browser, Mobile App, API)                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTPS/REST API
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │  ← Single Entry Point
                    │   (Port 8080)   │     Routes & Load Balances
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐        ┌──────▼──────┐      ┌─────▼─────┐
   │  User   │        │   Product   │      │   Order   │
   │ Service │        │   Service   │      │  Service  │
   │  :3001  │        │   :3002     │      │   :3003   │
   └────┬────┘        └──────┬──────┘      └─────┬─────┘
        │                    │                    │
   ┌────▼────────────────────▼────────────────────▼─────┐
   │              PostgreSQL Database                     │
   │  • ecommerce_users     • ecommerce_products         │
   │  • ecommerce_orders    • ecommerce_payments         │
   └─────────────────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Redis Cache    │
                    │   (Port 6379)   │
                    └─────────────────┘
```

### Service Communication Flow

1. **Client** → API Gateway (single entry point)
2. **API Gateway** → Routes request to appropriate microservice
3. **Microservice** → Processes business logic
4. **Microservice** → Communicates with other services if needed (via HTTP)
5. **Database/Redis** → Data persistence and caching
6. **Response** → Flows back through Gateway to Client

---

## 🛠️ Technology Stack

### Backend Framework
- **Python 3.11+** - Modern Python with type hints
- **FastAPI** - High-performance async web framework
- **Uvicorn** - ASGI server with async support
- **Pydantic** - Data validation and type safety

### Databases & Caching
- **PostgreSQL 15** - Primary relational database (ACID compliant)
- **Redis 7** - In-memory cache and session storage

### Authentication & Security
- **JWT (JSON Web Tokens)** - Stateless authentication
- **python-jose** - JWT encoding/decoding
- **passlib** - Password hashing (bcrypt)
- **CORS** - Cross-origin resource sharing

### DevOps & Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local development orchestration
- **Kubernetes** - Production container orchestration
- **GitHub Actions** - CI/CD pipeline
- **GitHub Container Registry (GHCR)** - Docker image registry

### Additional Libraries
- **httpx** - Async HTTP client for service-to-service communication
- **asyncpg** - Async PostgreSQL driver
- **python-dotenv** - Environment variable management

---

## ✨ Features

### Core Functionality
- ✅ **User Management**: Registration, authentication, profile management
- ✅ **Product Catalog**: CRUD operations, search, filtering, categorization
- ✅ **Order Processing**: Order creation, status tracking, item management
- ✅ **Payment Integration**: Payment processing (Stripe/PayPal ready)
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Auto-generated API Docs**: Swagger UI at `/docs` for all services

### Architecture Features
- ✅ **Microservices Architecture**: Independent, scalable services
- ✅ **API Gateway Pattern**: Single entry point with routing and load balancing
- ✅ **Database per Service**: Data isolation and independent scaling
- ✅ **Service-to-Service Communication**: HTTP/REST for inter-service calls
- ✅ **Containerization**: Docker for consistent deployments
- ✅ **Health Checks**: Built-in health monitoring endpoints

### DevOps Features
- ✅ **CI/CD Pipeline**: Automated testing and Docker image builds
- ✅ **Kubernetes Deployment**: Production-ready manifests
- ✅ **Multi-platform Images**: Linux/AMD64 and ARM64 support
- ✅ **Image Registry**: Automated pushes to GHCR

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (latest version)
- **kubectl** (for Kubernetes deployment)
- **Git** (for cloning the repository)

### Option 1: Docker Compose (Recommended for Local Development)

```bash
# Clone the repository
git clone https://github.com/Beepeen78/Multi-service-ecommerce-platform.git
cd Multi-service-ecommerce-platform

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Option 2: Kubernetes Deployment

```bash
# Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# Deploy databases
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Deploy services
kubectl apply -f k8s/api-gateway-deployment.yaml
# ... deploy other services similarly

# Access API Gateway
kubectl port-forward svc/api-gateway-service 8080:80 -n ecommerce-platform
```

### Access the Application

- **API Gateway**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

### Individual Services (Direct Access)

- **User Service**: http://localhost:3001/docs
- **Product Service**: http://localhost:3002/docs
- **Order Service**: http://localhost:3003/docs
- **Payment Service**: http://localhost:3004/docs

---

## 📁 Project Structure

```
Multi-Service E-Commerce Platform/
│
├── services/                      # Microservices
│   ├── api-gateway/              # API Gateway (Python/FastAPI)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── user-service/             # User management & authentication
│   ├── product-service/          # Product catalog
│   ├── order-service/            # Order processing
│   └── payment-service/          # Payment processing
│
├── k8s/                          # Kubernetes manifests
│   ├── namespace.yaml
│   ├── secrets.yaml
│   ├── configmap.yaml
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   └── api-gateway-deployment.yaml
│
├── scripts/                      # Utility scripts
│   └── init-db.sql              # Database initialization
│
├── .github/workflows/            # CI/CD pipelines
│   ├── docker-build.yml         # Automated Docker builds
│   └── ci-cd-complete.yml       # Full CI/CD pipeline
│
├── docker-compose.yml            # Docker Compose configuration
├── .gitignore
└── README.md                     # This file
```

---

## 📚 API Documentation

### Interactive API Documentation

All services provide **automatic Swagger UI** documentation:

- Visit `/docs` on any service for interactive API testing
- Visit `/redoc` for alternative documentation format
- OpenAPI schema available at `/openapi.json`

### Example API Calls

#### Register a User

```bash
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123",
    "name": "John Doe"
  }'
```

#### Login

```bash
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123"
  }'
```

#### Create a Product (Protected - requires JWT)

```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Gaming Laptop",
    "description": "High-performance gaming laptop",
    "price": 1299.99,
    "category": "Electronics",
    "stock_quantity": 50
  }'
```

#### Create an Order (Protected)

```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2}
    ],
    "shipping_address": "123 Main St, City, Country"
  }'
```

---

## 🚢 Deployment

### Development (Docker Compose)

```bash
docker-compose up -d
```

### Production (Kubernetes)

```bash
# Deploy infrastructure
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Deploy services
kubectl apply -f k8s/api-gateway-deployment.yaml
kubectl apply -f k8s/user-service-deployment.yaml
# ... deploy other services

# Check status
kubectl get pods -n ecommerce-platform
kubectl get services -n ecommerce-platform
```

### CI/CD Pipeline

The project includes GitHub Actions workflows that:

1. **On Push to Main**:
   - Run tests (if configured)
   - Build Docker images for all services
   - Push images to GitHub Container Registry (GHCR)
   - Tag images with `latest`, branch name, and commit SHA

2. **Automated Deployment**:
   - Images are available at: `ghcr.io/beepeen78/<service-name>:latest`
   - Kubernetes deployments pull from GHCR automatically

---

## 💪 Strengths

### 1. **Modern Architecture**
- **Microservices Pattern**: Services are independent, allowing for independent scaling and deployment
- **API Gateway**: Single entry point simplifies client interaction and provides centralized routing
- **Separation of Concerns**: Each service handles a single business domain

### 2. **Technology Choices**
- **FastAPI**: High performance, automatic documentation, type safety with Pydantic
- **Python**: Readable, maintainable, excellent for rapid development
- **Async Support**: Non-blocking I/O for better performance under load
- **PostgreSQL**: Reliable, ACID-compliant, excellent for transactional data

### 3. **Scalability**
- **Horizontal Scaling**: Each service can be scaled independently
- **Stateless Services**: Easy to replicate and load balance
- **Database per Service**: Independent database scaling strategies
- **Caching Layer**: Redis reduces database load

### 4. **Developer Experience**
- **Auto-generated Docs**: Swagger UI automatically generated from code
- **Type Safety**: Pydantic models provide runtime validation
- **Containerization**: Consistent environment across dev/staging/prod
- **Easy Testing**: Services can be tested in isolation

### 5. **Production Readiness**
- **Health Checks**: Built-in endpoints for monitoring
- **Container Orchestration**: Kubernetes manifests included
- **CI/CD Pipeline**: Automated builds and deployments
- **Security**: JWT authentication, password hashing, CORS support

### 6. **Maintainability**
- **Clear Structure**: Well-organized codebase
- **Documentation**: Comprehensive API documentation
- **Version Control**: Git-based workflow with GitHub
- **Docker**: Consistent deployments eliminate "works on my machine" issues

---

## ⚠️ Weaknesses & Future Improvements

### Current Limitations

1. **No Message Queue**
   - **Current**: Services communicate synchronously via HTTP
   - **Impact**: Tight coupling, potential cascading failures
   - **Improvement**: Implement RabbitMQ or Kafka for async communication

2. **Limited Monitoring & Observability**
   - **Current**: Basic health checks only
   - **Impact**: Difficult to debug production issues
   - **Improvement**: Add Prometheus, Grafana, distributed tracing (Jaeger)

3. **No Circuit Breaker Pattern**
   - **Current**: Services can fail and cause cascading failures
   - **Impact**: Poor resilience
   - **Improvement**: Implement circuit breakers (resilience4j, Hystrix)

4. **Authentication in Each Service**
   - **Current**: Each service validates JWT independently
   - **Impact**: Code duplication
   - **Improvement**: Centralize auth in API Gateway or use service mesh

5. **No Rate Limiting**
   - **Current**: No protection against DDoS or abuse
   - **Impact**: Vulnerable to abuse
   - **Improvement**: Add rate limiting at API Gateway

6. **Basic Error Handling**
   - **Current**: Simple error responses
   - **Impact**: Poor debugging experience
   - **Improvement**: Structured error responses, correlation IDs

7. **No Load Testing**
   - **Current**: No performance benchmarks
   - **Impact**: Unknown scalability limits
   - **Improvement**: Add load testing (Locust, k6)

8. **Limited Test Coverage**
   - **Current**: Minimal automated tests
   - **Impact**: Risk of regressions
   - **Improvement**: Unit tests, integration tests, E2E tests

### Future Enhancements

1. **Service Mesh** (Istio/Linkerd)
   - Advanced service-to-service communication
   - Automatic mTLS encryption
   - Advanced traffic management

2. **Event-Driven Architecture**
   - Event sourcing for order history
   - CQRS pattern for read/write separation

3. **Multi-Region Deployment**
   - Geographic distribution
   - CDN integration
   - Database replication

4. **Advanced Caching Strategies**
   - Redis cluster for high availability
   - Cache invalidation strategies
   - CDN for static assets

5. **Frontend Application**
   - React/Vue.js SPA
   - Mobile app (React Native)

6. **Advanced Features**
   - Real-time notifications (WebSockets)
   - Search service (Elasticsearch)
   - Recommendation engine (ML-based)

---

## 🎤 Presentation Points

### For Interviews / Presentations

#### **1. Project Overview (30 seconds)**
> "This is a microservices-based e-commerce platform built with Python and FastAPI. It demonstrates production-grade architecture with containerization, orchestration, and CI/CD. The system consists of 5+ independent services, each handling a specific business domain, communicating via HTTP/REST APIs."

#### **2. Architecture Decision (1 minute)**
> "I chose microservices over monolith because it allows for:
> - Independent scaling: Product service can scale during sales without scaling the entire system
> - Technology flexibility: Each service can use the best tool for its job
> - Team autonomy: Different teams can work on different services simultaneously
> - Fault isolation: A failure in one service doesn't bring down the entire platform"

#### **3. Technology Stack Justification (1 minute)**
> "FastAPI was chosen for its:
> - High performance: Comparable to Node.js and Go
> - Automatic API documentation: Reduces documentation overhead
> - Type safety: Pydantic provides runtime validation
> - Modern Python features: Async/await for non-blocking I/O
> 
> Docker ensures consistency across environments, and Kubernetes provides production-grade orchestration with auto-scaling and self-healing capabilities."

#### **4. Challenges Overcome (1 minute)**
> "Key challenges I addressed:
> - Service communication: Implemented HTTP-based inter-service calls with proper error handling
> - Database design: Separate databases per service for data isolation
> - Authentication: JWT tokens for stateless authentication across services
> - Deployment complexity: Solved with Docker and Kubernetes manifests
> - CI/CD: Automated builds and deployments via GitHub Actions"

#### **5. Scalability Demonstration (1 minute)**
> "The architecture supports horizontal scaling:
> - Each service can be scaled independently based on load
> - API Gateway distributes load across service instances
> - Database can be scaled with read replicas
> - Redis caching reduces database load significantly"

#### **6. Future Improvements (30 seconds)**
> "To make this production-ready, I would add:
> - Message queues for async communication
> - Monitoring and observability (Prometheus, Grafana)
> - Circuit breakers for resilience
> - Comprehensive test coverage
> - Rate limiting and security enhancements"

### Key Metrics to Mention

- **Services**: 5+ microservices
- **Languages**: Python 3.11+
- **Frameworks**: FastAPI
- **Databases**: PostgreSQL + Redis
- **Containers**: Fully containerized
- **CI/CD**: Automated via GitHub Actions
- **Deployment**: Kubernetes-ready

### Demonstration Flow

1. **Show Architecture Diagram**: Explain service communication
2. **Live Demo**: Start services with `docker-compose up`
3. **Show API Docs**: Demonstrate Swagger UI at `/docs`
4. **Make API Calls**: Show user registration, product creation, order creation
5. **Show Kubernetes Deployment**: `kubectl get pods -n ecommerce-platform`
6. **Show CI/CD**: GitHub Actions workflow runs

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the ISC License.

---

## 👤 Author

**Beepeen78**

- GitHub: [@Beepeen78](https://github.com/Beepeen78)
- Repository: [Multi-service-ecommerce-platform](https://github.com/Beepeen78/Multi-service-ecommerce-platform)

---

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Docker and Kubernetes communities
- All open-source contributors

---

## 📞 Contact & Support

For questions, issues, or contributions:

- **GitHub Issues**: [Open an issue](https://github.com/Beepeen78/Multi-service-ecommerce-platform/issues)
- **Documentation**: See `PROJECT_REPORT.md` for detailed architecture documentation

---

**⭐ If you find this project helpful, please give it a star!**

---

> **Built with ❤️ using Python, FastAPI, Docker, and Kubernetes**
