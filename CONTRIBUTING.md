# Contributing Guide

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Go 1.21+
- Python 3.11+
- kubectl
- Helm 3.x
- Minikube or Kubernetes cluster

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-org/ecommerce-platform.git
cd ecommerce-platform
```

2. **Start local infrastructure**
```bash
docker-compose up -d
```

3. **Run services locally**
```bash
# Node.js services
cd services/auth-service
npm install
npm run dev

# Go services
cd services/user-service
go run main.go

# Python services
cd services/inventory-service
pip install -r requirements.txt
python app.py
```

### Testing

```bash
# Run all tests
make test

# Run tests for specific service
make test SERVICE=auth-service
```

### Building Docker Images

```bash
# Build all services
make build

# Build specific service
make build SERVICE=auth-service
```

## Code Style

### Node.js
- Use ESLint configuration
- Follow Airbnb style guide
- Use async/await for async operations

### Go
- Use `gofmt` for formatting
- Follow Go best practices
- Add comments for exported functions

### Python
- Use Black for formatting
- Follow PEP 8 style guide
- Type hints for function parameters

## Git Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

### Commit Messages
- Use conventional commits format
- Examples:
  - `feat: add user profile endpoint`
  - `fix: resolve cart service memory leak`
  - `docs: update deployment guide`

## Pull Request Process

1. Update README.md if needed
2. Update CHANGELOG.md
3. Ensure CI/CD pipeline passes
4. Get at least one review approval
5. Merge to main branch

## Adding a New Service

1. Create service directory in `services/`
2. Implement service with health endpoint
3. Add Dockerfile
4. Create Helm template in `helm/ecommerce-platform/templates/`
5. Update `values.yaml`
6. Add to CI/CD pipeline
7. Update documentation

## Database Migrations

1. Create migration SQL file in `k8s/database/migrations/`
2. Update `init-schema.sql` if needed
3. Test migration locally
4. Document breaking changes

## Monitoring

- Add Prometheus metrics endpoints
- Add health check endpoints
- Log important events
- Add distributed tracing (optional)

## Security

- Never commit secrets
- Use environment variables for configuration
- Validate all inputs
- Use parameterized queries
- Follow OWASP guidelines

