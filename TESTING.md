# Testing Guide

This guide explains how to run and test the Multi-Service E-Commerce Platform.

## Starting the Services

### Using Docker Compose (Recommended)

**Start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f user-service
docker-compose logs -f product-service
docker-compose logs -f order-service
```

**Stop all services:**
```bash
docker-compose down
```

**Rebuild and restart:**
```bash
docker-compose up -d --build
```

**Check service status:**
```bash
docker-compose ps
```

## API Endpoints

All endpoints are accessible through the API Gateway at `http://localhost:8080`

### API Gateway
- **Info:** `GET http://localhost:8080/`
- **Health:** `GET http://localhost:8080/health`

### User Service (`/api/users`)
- **Register:** `POST http://localhost:8080/api/users/register`
- **Login:** `POST http://localhost:8080/api/users/login`
- **Profile:** `GET http://localhost:8080/api/users/profile` (Requires JWT token)
- **List Users:** `GET http://localhost:8080/api/users/users` (for testing)

### Product Service (`/api/products`)
- **Get All Products:** `GET http://localhost:8080/api/products`
- **Get Product by ID:** `GET http://localhost:8080/api/products/:id`
- **Search Products:** `GET http://localhost:8080/api/products?search=laptop`
- **Filter by Category:** `GET http://localhost:8080/api/products?category=electronics`
- **Create Product:** `POST http://localhost:8080/api/products`
- **Update Product:** `PUT http://localhost:8080/api/products/:id`
- **Delete Product:** `DELETE http://localhost:8080/api/products/:id`

### Order Service (`/api/orders`)
- **Health Check:** `GET http://localhost:8080/api/orders/health`
- **Get User Orders:** `GET http://localhost:8080/api/orders` (Requires JWT token)
- **Get Order by ID:** `GET http://localhost:8080/api/orders/:id` (Requires JWT token)
- **Create Order:** `POST http://localhost:8080/api/orders` (Requires JWT token)
- **Update Order Status:** `PATCH http://localhost:8080/api/orders/:id/status` (Requires JWT token)

## Testing with cURL

### 1. Register a New User

```bash
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123",
    "name": "John Doe"
  }'
```

**Expected Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Save the token** from the response for authenticated requests!

### 2. Login

```bash
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### 3. Get User Profile (Requires Authentication)

```bash
curl -X GET http://localhost:8080/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Create a Product

```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "category": "electronics",
    "stock_quantity": 50
  }'
```

### 5. Get All Products

```bash
curl -X GET http://localhost:8080/api/products
```

### 6. Get Product by ID

```bash
curl -X GET http://localhost:8080/api/products/1
```

### 7. Create an Order (Requires Authentication)

```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ],
    "shipping_address": "123 Main St, City, Country"
  }'
```

### 8. Get User Orders (Requires Authentication)

```bash
curl -X GET http://localhost:8080/api/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 9. Update Order Status (Requires Authentication)

```bash
curl -X PATCH http://localhost:8080/api/orders/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "status": "processing"
  }'
```

Valid statuses: `pending`, `processing`, `shipped`, `delivered`, `cancelled`

## Testing with PowerShell (Windows)

### Register User

```powershell
$body = @{
    email = "john@example.com"
    password = "password123"
    name = "John Doe"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8080/api/users/register" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

$response.Content | ConvertFrom-Json
```

### Login and Save Token

```powershell
$body = @{
    email = "john@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8080/api/users/login" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

$result = $response.Content | ConvertFrom-Json
$token = $result.token
Write-Host "Token: $token"
```

### Create Product

```powershell
$body = @{
    name = "Laptop"
    description = "High-performance laptop"
    price = 999.99
    category = "electronics"
    stock_quantity = 50
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/api/products" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Get Products

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8080/api/products"
$response.Content | ConvertFrom-Json
```

### Create Order

```powershell
$body = @{
    items = @(
        @{
            product_id = 1
            quantity = 2
        }
    )
    shipping_address = "123 Main St, City, Country"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/api/orders" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -Headers @{Authorization = "Bearer $token"}
```

## Testing with Postman

1. **Import Collection:**
   - Create a new collection
   - Add requests for each endpoint
   - Set base URL: `http://localhost:8080`

2. **Authentication Setup:**
   - Register/Login first
   - Copy the JWT token
   - For protected endpoints, add header:
     - Key: `Authorization`
     - Value: `Bearer YOUR_TOKEN_HERE`

3. **Environment Variables:**
   - Create an environment
   - Add variable: `token` = your JWT token
   - Use `{{token}}` in Authorization header

## Testing with Browser

You can test GET endpoints directly in your browser:

- API Gateway Info: http://localhost:8080/
- Health Check: http://localhost:8080/health
- Products: http://localhost:8080/api/products
- User Service Health: http://localhost:8080/api/users/health (if implemented)

For POST/PUT/DELETE requests, use browser developer tools or a tool like Postman.

## Complete Testing Workflow

### Step 1: Start Services
```bash
docker-compose up -d
```

### Step 2: Verify Services are Running
```bash
docker-compose ps
# All services should show "Up" status
```

### Step 3: Test API Gateway
```bash
curl http://localhost:8080/health
```

### Step 4: Register a User
```bash
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

### Step 5: Login and Get Token
```bash
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Step 6: Create Products
```bash
# Create multiple products
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","description":"Gaming laptop","price":1299.99,"category":"electronics","stock_quantity":10}'

curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Mouse","description":"Wireless mouse","price":29.99,"category":"electronics","stock_quantity":50}'
```

### Step 7: List Products
```bash
curl http://localhost:8080/api/products
```

### Step 8: Create an Order (use token from step 5)
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"items":[{"product_id":1,"quantity":1}],"shipping_address":"123 Test St"}'
```

### Step 9: View Orders
```bash
curl http://localhost:8080/api/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs [service-name]

# Rebuild containers
docker-compose build [service-name]
docker-compose up -d [service-name]
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Create databases manually if needed
docker-compose exec postgres psql -U user -d ecommerce -c "CREATE DATABASE ecommerce_users;"
docker-compose exec postgres psql -U user -d ecommerce -c "CREATE DATABASE ecommerce_products;"
docker-compose exec postgres psql -U user -d ecommerce -c "CREATE DATABASE ecommerce_orders;"
```

### Port Already in Use

If ports are already in use, you can:
1. Stop other services using those ports
2. Change ports in `docker-compose.yml`
3. Check what's using the port: `netstat -ano | findstr :8080` (Windows)

### Authentication Errors

- Make sure you're including the `Authorization: Bearer TOKEN` header
- Check that the token hasn't expired
- Verify the token format: `Bearer <token>` (with space)

## Health Checks

Check service health:

```bash
# API Gateway
curl http://localhost:8080/health

# User Service
curl http://localhost:3001/health

# Product Service
curl http://localhost:3002/health

# Order Service
curl http://localhost:3003/health

# Through API Gateway
curl http://localhost:8080/api/users/health
curl http://localhost:8080/api/products/health
curl http://localhost:8080/api/orders/health
```

## Next Steps

1. Test all CRUD operations
2. Test error scenarios (invalid data, missing fields, etc.)
3. Test authentication and authorization
4. Load testing (if needed)
5. Integration testing between services

