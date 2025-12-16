# Quick Kubernetes Deployment (Without Helm)

Since you have Kubernetes running but Helm is not installed, here's how to deploy using **kubectl only**.

---

## ✅ Prerequisites Check

You have:
- ✅ Kubernetes cluster running (Docker Desktop)
- ✅ kubectl installed and working
- ❌ Helm (not needed for this method)

---

## 🚀 Quick Deployment Steps

### Step 1: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 2: Create Secrets

First, edit `k8s/secrets.yaml` with your actual secrets, then:

```bash
kubectl apply -f k8s/secrets.yaml
```

### Step 3: Create ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

### Step 4: Deploy Databases

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce-platform --timeout=300s
```

### Step 5: Deploy API Gateway

```bash
kubectl apply -f k8s/api-gateway-deployment.yaml
```

### Step 6: Check Status

```bash
# Check all resources
kubectl get all -n ecommerce-platform

# Check pods
kubectl get pods -n ecommerce-platform

# View logs
kubectl logs -f deployment/api-gateway -n ecommerce-platform
```

---

## 📝 Note: Create Service Deployments

You'll need to create deployment files for other services (user-service, product-service, etc.) if they don't exist. Use `k8s/service-deployment-template.yaml` as a template.

---

## 🔧 Alternative: Install Helm (Optional)

If you want to use Helm (easier deployment), install it:

### Windows (PowerShell):

```powershell
# Using Chocolatey
choco install kubernetes-helm

# Or using Scoop
scoop install helm

# Or download from: https://github.com/helm/helm/releases
```

### After Installing Helm:

```bash
# Verify installation
helm version

# Deploy with Helm
cd helm/ecommerce-platform
helm install ecommerce-platform . -n ecommerce --create-namespace
```

---

## 🎯 Quick Test

After deploying, test with:

```bash
# Port forward to access API Gateway
kubectl port-forward svc/api-gateway 8080:8080 -n ecommerce-platform

# In another terminal, test
curl http://localhost:8080/health
```

---

**You can deploy now using kubectl! No Helm needed! 🚀**

