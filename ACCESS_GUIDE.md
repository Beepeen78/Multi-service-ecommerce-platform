# How to Access Your Deployed Application

## ✅ Port Forwarding Active

Your API Gateway is now accessible via port forwarding:
- **Command**: `kubectl port-forward svc/api-gateway-service 8080:80 -n ecommerce-platform`
- **Status**: Forwarding from 127.0.0.1:8080 -> 8080

---

## 🌐 Access Points

### 1. API Gateway (Main Entry Point)
- **URL**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

### 2. API Endpoints

Once port forwarding is active, you can access:

```
http://localhost:8080/api/users/*      - User service endpoints
http://localhost:8080/api/products/*   - Product service endpoints
http://localhost:8080/api/orders/*     - Order service endpoints
http://localhost:8080/api/payments/*   - Payment service endpoints
```

---

## 🧪 Test the API

### Using Browser:
1. Open: http://localhost:8080/docs
2. Interactive Swagger UI for testing all endpoints

### Using curl:
```bash
# Health check
curl http://localhost:8080/health

# API info
curl http://localhost:8080/

# Test user registration (example)
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

---

## 📊 Current Deployment Status

### Running Services:
- ✅ **API Gateway**: 2 replicas running
- ✅ **PostgreSQL**: Running
- ✅ **Redis**: Running

### Services Not Yet Deployed:
- ⏳ User Service
- ⏳ Product Service
- ⏳ Order Service
- ⏳ Payment Service

**Note**: The API Gateway is running but backend services need to be deployed to handle requests.

---

## 🔄 Keep Port Forwarding Active

Port forwarding runs in the foreground. To keep it active:

1. **Run in background** (PowerShell):
   ```powershell
   Start-Job -ScriptBlock { kubectl port-forward svc/api-gateway-service 8080:80 -n ecommerce-platform }
   ```

2. **Or use a separate terminal**:
   - Open another terminal window
   - Keep the port-forward command running there
   - Use the first terminal for other commands

---

## 🚀 Next Steps

### To Deploy Backend Services:

1. **Create deployment files** for each service:
   - `k8s/user-service-deployment.yaml`
   - `k8s/product-service-deployment.yaml`
   - `k8s/order-service-deployment.yaml`
   - `k8s/payment-service-deployment.yaml`

2. **Use the template**:
   ```bash
   # Copy template
   cp k8s/service-deployment-template.yaml k8s/user-service-deployment.yaml
   
   # Edit and replace:
   # - SERVICE_NAME → user-service
   # - SERVICE_PORT → 3001
   # - image: ghcr.io/beepeen78/user-service:latest
   ```

3. **Deploy**:
   ```bash
   kubectl apply -f k8s/user-service-deployment.yaml
   # Repeat for other services
   ```

---

## 🐛 Troubleshooting

### Port Forward Stops Working:
```bash
# Restart port forwarding
kubectl port-forward svc/api-gateway-service 8080:80 -n ecommerce-platform
```

### Cannot Access API:
1. Check if port forwarding is active
2. Verify pods are running: `kubectl get pods -n ecommerce-platform`
3. Check logs: `kubectl logs -f deployment/api-gateway -n ecommerce-platform`

### Backend Services Not Responding:
- Deploy backend services first (see Next Steps above)
- Check service endpoints in API Gateway logs

---

## 📝 Summary

✅ **API Gateway is accessible at**: http://localhost:8080  
✅ **Interactive docs at**: http://localhost:8080/docs  
⏳ **Next**: Deploy backend services to handle API requests

**Your Kubernetes deployment is working! 🎉**

