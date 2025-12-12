# Testing Guide

This guide covers all aspects of testing the e-commerce platform.

## Table of Contents

1. [Local Testing](#local-testing)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [API Testing](#api-testing)
5. [Kubernetes Testing](#kubernetes-testing)
6. [Load Testing](#load-testing)
7. [End-to-End Testing](#end-to-end-testing)

## Local Testing

### Prerequisites
```bash
# Install dependencies
npm install -g newman  # For API testing
```

### Start Local Environment
```bash
# Start infrastructure (PostgreSQL, Redis, Kafka)
docker-compose up -d

# Wait for services to be ready
sleep 30

# Verify infrastructure
docker-compose ps
```

### Test Individual Services

#### Auth Service
```bash
cd services/auth-service
npm install
npm test
npm start  # In another terminal
```

#### User Service
```bash
cd services/user-service
go test ./...
go run main.go  # In another terminal
```

#### Product Service
```bash
cd services/product-service
npm install
npm test
npm start  # In another terminal
```

#### Python Services
```bash
cd services/inventory-service
pip install -r requirements.txt
pytest  # If tests exist
python app.py  # In another terminal
```

## Unit Tests

### Node.js Services

Run tests for all Node.js services:
```bash
make test SERVICE=auth-service
make test SERVICE=product-service
make test SERVICE=cart-service
make test SERVICE=payment-service
```

### Go Services

Run tests for Go services:
```bash
cd services/user-service
go test -v ./...

cd services/order-service
go test -v ./...
```

### Python Services

Run tests for Python services:
```bash
cd services/inventory-service
pytest -v

cd services/notification-service
pytest -v

cd services/recommendation-service
pytest -v
```

## Integration Tests

### Test Database Connection
```bash
# Test PostgreSQL
docker exec -it sustainability_sql_project-postgres-1 psql -U ecommerce -d ecommerce -c "SELECT version();"

# Test Redis
docker exec -it sustainability_sql_project-redis-1 redis-cli ping
```

### Test Service Communication

#### Test Auth → User Service Flow
```bash
# 1. Register user
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'

# 2. Login and get token
TOKEN=$(curl -s -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' | jq -r '.token')

# 3. Get user profile
curl -X GET "http://localhost:3002/api/users?id=1" \
  -H "Authorization: Bearer $TOKEN"
```

## API Testing

### Using cURL

#### Complete E-Commerce Flow Test
```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=== E-Commerce Platform API Test ==="

# 1. Health Checks
echo -e "\n${GREEN}1. Testing Health Endpoints${NC}"
curl -s http://localhost:3001/health | jq .
curl -s http://localhost:3002/health | jq .
curl -s http://localhost:3003/health | jq .

# 2. Register User
echo -e "\n${GREEN}2. Registering User${NC}"
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "name": "Test User"
  }')
echo $REGISTER_RESPONSE | jq .

USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.user.id')
TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.token')

# 3. Login
echo -e "\n${GREEN}3. Logging In${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123"
  }')
echo $LOGIN_RESPONSE | jq .

# 4. Get Products
echo -e "\n${GREEN}4. Getting Products${NC}"
curl -s http://localhost:3003/api/products | jq .

# 5. Add to Cart
echo -e "\n${GREEN}5. Adding to Cart${NC}"
curl -s -X POST http://localhost:3005/api/cart/$USER_ID/items \
  -H "Content-Type: application/json" \
  -d '{
    "productId": 1,
    "quantity": 2,
    "price": 29.99
  }' | jq .

# 6. Get Cart
echo -e "\n${GREEN}6. Getting Cart${NC}"
curl -s http://localhost:3005/api/cart/$USER_ID | jq .

# 7. Create Order
echo -e "\n${GREEN}7. Creating Order${NC}"
ORDER_RESPONSE=$(curl -s -X POST http://localhost:3006/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "userId": '$USER_ID',
    "total": 59.98,
    "items": [
      {
        "productId": 1,
        "quantity": 2,
        "price": 29.99
      }
    ]
  }')
echo $ORDER_RESPONSE | jq .

ORDER_ID=$(echo $ORDER_RESPONSE | jq -r '.id')

# 8. Process Payment
echo -e "\n${GREEN}8. Processing Payment${NC}"
curl -s -X POST http://localhost:3007/api/payments \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": '$ORDER_ID',
    "amount": 59.98,
    "paymentMethod": "credit_card",
    "cardToken": "tok_test123"
  }' | jq .

# 9. Get Notifications
echo -e "\n${GREEN}9. Getting Notifications${NC}"
sleep 2  # Wait for Kafka consumer
curl -s http://localhost:3008/api/notifications/$USER_ID | jq .

# 10. Get Recommendations
echo -e "\n${GREEN}10. Getting Recommendations${NC}"
curl -s http://localhost:3009/api/recommendations/$USER_ID | jq .

echo -e "\n${GREEN}=== Test Complete ===${NC}"
```

Save as `test-api.sh`, make executable, and run:
```bash
chmod +x test-api.sh
./test-api.sh
```

### Using Postman/Newman

Create a Postman collection and run with Newman:
```bash
newman run tests/postman/ecommerce-api.json \
  --environment tests/postman/local-env.json \
  --reporters cli,json
```

### Using HTTPie

```bash
# Install HTTPie
pip install httpie

# Test endpoints
http GET localhost:3001/health
http POST localhost:3001/api/auth/register email=test@example.com password=pass123 name="Test User"
```

## Kubernetes Testing

### Deploy to Test Cluster
```bash
# Build and push images
make build

# Deploy with Helm
cd helm/ecommerce-platform
helm install ecommerce-test . \
  --namespace ecommerce-test \
  --create-namespace \
  --set ingress.enabled=false
```

### Test Pods
```bash
# Check all pods are running
kubectl get pods -n ecommerce-test

# Check pod logs
kubectl logs -f deployment/auth-service -n ecommerce-test

# Test service endpoints
kubectl port-forward svc/auth-service 3001:3001 -n ecommerce-test
curl http://localhost:3001/health
```

### Test HPA
```bash
# Generate load
kubectl run -i --tty load-generator --rm \
  --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://product-service:3003/api/products; done"

# Watch HPA scale
kubectl get hpa -n ecommerce-test -w
```

### Test KEDA
```bash
# Check KEDA scaled objects
kubectl get scaledobjects -n ecommerce-test

# Send messages to Kafka to trigger scaling
kubectl exec -it kafka-0 -n ecommerce-test -- \
  kafka-console-producer --broker-list localhost:9092 --topic orders
```

## Load Testing

### Using Apache Bench (ab)
```bash
# Install Apache Bench
# Ubuntu/Debian: sudo apt-get install apache2-utils
# macOS: brew install httpd

# Test product service
ab -n 1000 -c 10 http://localhost:3003/api/products

# Test auth service
ab -n 500 -c 5 -p register.json -T application/json \
  http://localhost:3001/api/auth/register
```

### Using k6
```bash
# Install k6
# https://k6.io/docs/getting-started/installation/

# Run load test
k6 run tests/load/product-service.js
```

### Using Locust
```bash
# Install Locust
pip install locust

# Run load test
cd tests/load
locust -f ecommerce_load_test.py --host=http://localhost
```

## End-to-End Testing

### Complete User Journey Test
```bash
#!/bin/bash

# This tests the complete user journey:
# 1. Register → 2. Login → 3. Browse Products → 4. Add to Cart
# 5. Checkout → 6. Pay → 7. Receive Notification → 8. Get Recommendations

BASE_URL="http://localhost"

# Helper function
test_endpoint() {
  local method=$1
  local url=$2
  local data=$3
  local expected_status=$4
  
  if [ -z "$data" ]; then
    response=$(curl -s -w "\n%{http_code}" -X $method "$url")
  else
    response=$(curl -s -w "\n%{http_code}" -X $method "$url" \
      -H "Content-Type: application/json" \
      -d "$data")
  fi
  
  status_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  if [ "$status_code" == "$expected_status" ]; then
    echo "✓ $url - Status: $status_code"
    echo "$body" | jq . 2>/dev/null || echo "$body"
    return 0
  else
    echo "✗ $url - Expected $expected_status, got $status_code"
    echo "$body"
    return 1
  fi
}

# Run E2E test
echo "Starting E2E Test..."

# 1. Register
REGISTER_DATA='{"email":"e2e@test.com","password":"test123","name":"E2E User"}'
REGISTER_RESPONSE=$(test_endpoint POST "$BASE_URL:3001/api/auth/register" "$REGISTER_DATA" 201)
USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.user.id')
TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.token')

# 2. Login
LOGIN_DATA='{"email":"e2e@test.com","password":"test123"}'
test_endpoint POST "$BASE_URL:3001/api/auth/login" "$LOGIN_DATA" 200

# 3. Browse Products
test_endpoint GET "$BASE_URL:3003/api/products" "" 200

# 4. Add to Cart
CART_DATA='{"productId":1,"quantity":1,"price":19.99}'
test_endpoint POST "$BASE_URL:3005/api/cart/$USER_ID/items" "$CART_DATA" 200

# 5. Create Order
ORDER_DATA="{\"userId\":$USER_ID,\"total\":19.99,\"items\":[{\"productId\":1,\"quantity\":1,\"price\":19.99}]}"
ORDER_RESPONSE=$(test_endpoint POST "$BASE_URL:3006/api/orders" "$ORDER_DATA" 201)
ORDER_ID=$(echo "$ORDER_RESPONSE" | jq -r '.id')

# 6. Process Payment
PAYMENT_DATA="{\"orderId\":$ORDER_ID,\"amount\":19.99,\"paymentMethod\":\"credit_card\"}"
test_endpoint POST "$BASE_URL:3007/api/payments" "$PAYMENT_DATA" 201

# 7. Check Notifications
sleep 3  # Wait for Kafka
test_endpoint GET "$BASE_URL:3008/api/notifications/$USER_ID" "" 200

# 8. Get Recommendations
test_endpoint GET "$BASE_URL:3009/api/recommendations/$USER_ID" "" 200

echo "E2E Test Complete!"
```

## Test Coverage

### Generate Coverage Reports

#### Node.js
```bash
cd services/auth-service
npm test -- --coverage
```

#### Go
```bash
cd services/user-service
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

#### Python
```bash
cd services/inventory-service
pytest --cov=. --cov-report=html
```

## Continuous Testing

Tests run automatically in CI/CD pipeline:
- Unit tests on every commit
- Integration tests on pull requests
- E2E tests before deployment
- Load tests on staging environment

## Troubleshooting Tests

### Service Not Responding
```bash
# Check if service is running
docker ps | grep service-name
kubectl get pods -n ecommerce-test

# Check logs
docker logs container-name
kubectl logs deployment/service-name -n ecommerce-test
```

### Database Connection Issues
```bash
# Test database connection
docker exec -it postgres psql -U ecommerce -d ecommerce -c "SELECT 1;"
```

### Redis Connection Issues
```bash
# Test Redis
docker exec -it redis redis-cli ping
```

### Kafka Issues
```bash
# Check Kafka topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clean State**: Reset database/Redis between tests
3. **Mock External Services**: Use mocks for payment gateways
4. **Test Data**: Use fixtures for consistent test data
5. **Error Cases**: Test both success and failure scenarios
6. **Performance**: Include performance benchmarks
7. **Security**: Test authentication and authorization

