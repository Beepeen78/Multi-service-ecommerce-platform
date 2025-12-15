# Quick Start Guide

## Understanding URLs

### ⚠️ Important: Two Types of URLs

**1. Internal Docker URLs (for containers to talk to each other):**
- `http://user-service:3001`
- `http://product-service:3002`
- `http://order-service:3003`
- These ONLY work INSIDE the Docker network
- These are what you see in API Gateway logs
- ❌ DON'T use these in your browser

**2. Host Machine URLs (for you to access from browser/terminal):**
- `http://localhost:3001` - User Service
- `http://localhost:3002` - Product Service  
- `http://localhost:3003` - Order Service
- `http://localhost:8080` - API Gateway (main entry point)
- ✅ USE THESE in your browser/Postman/curl

## Quick Test

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Check Status
```bash
docker-compose ps
```

### 3. Test in Browser
Open these URLs:
- http://localhost:8080 - API Gateway info
- http://localhost:8080/api/products - Get products (GET works!)

### 4. Register User (PowerShell)
```powershell
$body = '{"email":"test@example.com","password":"test123","name":"Test User"}'
Invoke-RestMethod -Uri "http://localhost:3001/register" -Method Post -Body $body -ContentType "application/json"
```

### 5. Create Product (PowerShell)
```powershell
$body = '{"name":"Laptop","description":"Gaming laptop","price":999.99,"category":"electronics","stock_quantity":10}'
Invoke-RestMethod -Uri "http://localhost:3002/" -Method Post -Body $body -ContentType "application/json"
```

### 6. View Products
Open in browser: http://localhost:8080/api/products

## Why You See Duplicate Logs

The API Gateway might log startup messages multiple times if:
- Service restarts
- Multiple instances running
- Code reloads during development

This is normal and doesn't affect functionality.

## Direct Service Access (Works Now!)

Since API Gateway has timeout issues with POST requests, use direct access:

| Service | Direct URL | Main Endpoints |
|---------|-----------|----------------|
| User Service | http://localhost:3001 | `/register`, `/login`, `/profile` |
| Product Service | http://localhost:3002 | `/` (GET all, POST create) |
| Order Service | http://localhost:3003 | `/` (GET all, POST create) |
| API Gateway | http://localhost:8080 | `/api/*` (GET works, POST times out) |

## Working Test Script

Run the working test script:
```powershell
.\scripts\test-working.ps1
```

This uses direct service access and works perfectly!

