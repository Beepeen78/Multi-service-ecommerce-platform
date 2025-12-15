# Multi-Service E-Commerce Platform (Python/FastAPI)

A microservices-based e-commerce platform built entirely with **Python and FastAPI**.

## 🏗️ Architecture

This platform consists of the following services:

- **API Gateway** - Single entry point for all client requests (Python/FastAPI)
- **User Service** - User management and authentication (Python/FastAPI)
- **Product Service** - Product catalog management (Python/FastAPI)
- **Order Service** - Order processing and management (Python/FastAPI)
- **Payment Service** - Payment processing (Python/FastAPI)

### Infrastructure

- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development, optional)

### Start All Services

```bash
docker-compose up -d
```

### Check Service Status

```bash
docker-compose ps
```

### View Logs

```bash
docker-compose logs -f
```

### Stop Services

```bash
docker-compose down
```

## 📁 Project Structure

```
.
├── services/              # Python/FastAPI microservices
│   ├── api-gateway/      # API Gateway service
│   ├── user-service/     # User management service
│   ├── product-service/  # Product catalog service
│   ├── order-service/    # Order processing service
│   └── payment-service/  # Payment processing service
├── k8s/                  # Kubernetes deployment manifests
├── nginx/                # Nginx configuration (optional)
├── scripts/              # Utility scripts
├── docker-compose.yml    # Docker Compose configuration
└── README.md            # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.11** - Programming language
- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **asyncpg** - Async PostgreSQL driver
- **httpx** - Async HTTP client

### Authentication & Security
- **python-jose** - JWT token handling
- **passlib** - Password hashing (bcrypt)

### Database
- **PostgreSQL 15** - Primary database
- **Redis 7** - Caching and session storage

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Kubernetes** - Container orchestration (production)

## 🌐 API Endpoints

### API Gateway
- **URL:** http://localhost:8080
- **Health:** http://localhost:8080/health
- **Docs:** http://localhost:8080/docs

### Individual Services

All services provide auto-generated Swagger UI documentation at `/docs`:

- **User Service:** http://localhost:3001/docs
- **Product Service:** http://localhost:3002/docs
- **Order Service:** http://localhost:3003/docs
- **Payment Service:** http://localhost:3004/docs

### API Routes (via Gateway)

- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/profile` - Get user profile (requires JWT)
- `GET /api/products` - Get all products
- `POST /api/products` - Create product
- `GET /api/products/{id}` - Get product by ID
- `POST /api/orders` - Create order (requires JWT)
- `GET /api/orders` - Get user orders (requires JWT)
- `POST /api/payments` - Process payment (requires JWT)

## 🔐 Environment Variables

Key environment variables (see `docker-compose.yml` for full list):

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `REDIS_URL` - Redis connection string
- `PORT` - Service port (defaults provided)

## 🧪 Testing

### Quick Test

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Register a user:**
   ```bash
   curl -X POST http://localhost:8080/api/users/register \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"test123","name":"Test User"}'
   ```

3. **Create a product:**
   ```bash
   curl -X POST http://localhost:8080/api/products \
     -H "Content-Type: application/json" \
     -d '{"name":"Laptop","description":"Gaming laptop","price":999.99,"category":"Electronics","stock_quantity":10}'
   ```

4. **View all products:**
   ```bash
   curl http://localhost:8080/api/products
   ```

## 📚 Documentation

- **API Documentation:** Available at `/docs` on each service (Swagger UI)
- **Project Report:** See `PROJECT_REPORT.md` for detailed architecture and interview guide
- **Architecture Diagrams:** See `ARCHITECTURE_DIAGRAM.txt` for visual diagrams

## 🔧 Development

### Running Services Locally (without Docker)

1. **Install dependencies:**
   ```bash
   cd services/user-service
   pip install -r requirements.txt
   ```

2. **Run service:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 3001 --reload
   ```

3. **Ensure infrastructure is running:**
   - PostgreSQL on port 5432
   - Redis on port 6379

## 🚢 Deployment

### Docker Compose (Recommended for Development/Testing)

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

## ✨ Features

- ✅ **Microservices Architecture** - Independent, scalable services
- ✅ **FastAPI Framework** - High-performance async API framework
- ✅ **Auto-generated API Docs** - Swagger UI for all services
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Database per Service** - Data isolation and independence
- ✅ **Docker Containerization** - Easy deployment and scaling
- ✅ **Health Checks** - Built-in health monitoring
- ✅ **Type Safety** - Pydantic models for validation

## 📝 License

ISC

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
