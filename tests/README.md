# Testing Quick Reference

## Quick Start

### 1. Start Services Locally
```bash
docker-compose up -d
sleep 30  # Wait for services to start
```

### 2. Run API Test Suite
```bash
# On Linux/Mac
./tests/api/test-ecommerce-flow.sh

# On Windows (using Git Bash or WSL)
bash tests/api/test-ecommerce-flow.sh
```

### 3. Run Unit Tests
```bash
# Node.js services
cd services/auth-service && npm test
cd services/product-service && npm test

# Go services
cd services/user-service && go test ./...
cd services/order-service && go test ./...

# Python services
cd services/inventory-service && pytest
```

## Test Files

- `test-ecommerce-flow.sh` - Complete E2E API test
- `k6-product-service.js` - Load testing with k6
- Service-specific tests in each service directory

## Prerequisites

- Docker and Docker Compose
- jq (for JSON parsing) - `brew install jq` or `apt-get install jq`
- curl
- Node.js, Go, Python (for unit tests)

## Manual Testing

See [TESTING.md](../TESTING.md) for comprehensive testing guide.

