# API Testing

## Quick Test

Run the complete E2E test suite:

```bash
# Linux/Mac
./test-ecommerce-flow.sh

# Windows (Git Bash or WSL)
bash test-ecommerce-flow.sh
```

## What It Tests

The test script validates:

1. ✅ Health checks for all 9 services
2. ✅ User registration
3. ✅ User login
4. ✅ Token verification
5. ✅ Product listing
6. ✅ Product details
7. ✅ Add to cart
8. ✅ View cart
9. ✅ Create order
10. ✅ Process payment
11. ✅ Check notifications
12. ✅ Get recommendations
13. ✅ Inventory management

## Prerequisites

- All services running (via `docker-compose up -d`)
- `jq` installed for JSON parsing
- `curl` available

## Expected Output

```
=== E-Commerce Platform API Test Suite ===

1. Testing Health Endpoints
✓ GET http://localhost:3001/health - Status: 200
✓ GET http://localhost:3002/health - Status: 200
...

=== Test Summary ===
Passed: 15
Failed: 0
Success Rate: 100%

All tests passed! ✓
```

## Troubleshooting

### Service Not Responding
```bash
# Check if services are running
docker-compose ps

# Check service logs
docker-compose logs auth-service
```

### jq Not Found
Install jq:
- macOS: `brew install jq`
- Ubuntu/Debian: `sudo apt-get install jq`
- Windows: Use WSL or Git Bash

### Connection Refused
Ensure services are started:
```bash
docker-compose up -d
# Wait 30 seconds for services to be ready
```

