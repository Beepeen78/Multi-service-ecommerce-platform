# Kubernetes Deployment Guide

Complete guide for deploying the Multi-Service E-Commerce Platform to Kubernetes.

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ **Kubernetes cluster** (local or cloud)
  - Minikube (local development)
  - Kind (local development)
  - GKE, EKS, AKS (cloud)
  - Docker Desktop with Kubernetes enabled

- ✅ **kubectl** installed and configured
  ```bash
  kubectl version --client
  kubectl cluster-info
  ```

- ✅ **Helm 3.x** installed (recommended)
  ```bash
  helm version
  ```

- ✅ **Docker images** built and pushed to registry
  - Images should be in GitHub Container Registry (GHCR)
  - Or your own container registry

---

## 🎯 Deployment Methods

You have **two options**:

### Option 1: Using Helm Charts (Recommended)
- Easier to manage
- Single command deployment
- Handles all resources

### Option 2: Using kubectl (Direct)
- More control
- Step-by-step deployment
- Good for learning

---

## 🚀 Method 1: Deploy with Helm (Recommended)

### Step 1: Update Helm Values

Edit `helm/ecommerce-platform/values.yaml` to use your images:

```yaml
# Update image registry
global:
  imageRegistry: "ghcr.io/beepeen78"  # Your GitHub username

# Or if using Docker Hub
# global:
#   imageRegistry: "docker.io/yourusername"
```

Update each service's image repository:

```yaml
services:
  user:
    image:
      repository: ghcr.io/beepeen78/user-service
      tag: latest  # or specific tag/version
  
  product:
    image:
      repository: ghcr.io/beepeen78/product-service
      tag: latest
  # ... repeat for other services
```

### Step 2: Deploy Infrastructure First

```bash
# Deploy PostgreSQL (if not using external database)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --namespace ecommerce \
  --create-namespace \
  --set auth.postgresPassword=ecommerce123 \
  --set auth.database=ecommerce

# Deploy Redis (if not using external Redis)
helm install redis bitnami/redis \
  --namespace ecommerce \
  --set auth.enabled=false
```

### Step 3: Deploy Application with Helm

```bash
# Navigate to helm chart directory
cd helm/ecommerce-platform

# Deploy all services
helm install ecommerce-platform . \
  --namespace ecommerce \
  --create-namespace \
  --wait \
  --timeout 10m

# Or upgrade if already installed
helm upgrade --install ecommerce-platform . \
  --namespace ecommerce \
  --create-namespace \
  --wait \
  --timeout 10m
```

### Step 4: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n ecommerce

# Check services
kubectl get svc -n ecommerce

# Check ingress
kubectl get ingress -n ecommerce

# View logs
kubectl logs -f deployment/user-service -n ecommerce
```

### Step 5: Access the Application

```bash
# Get service URLs
kubectl get ingress -n ecommerce

# Port forward for local access
kubectl port-forward svc/api-gateway 8080:8080 -n ecommerce

# Access at http://localhost:8080
```

---

## 🔧 Method 2: Deploy with kubectl (Step-by-Step)

### Step 1: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 2: Create Secrets

Edit `k8s/secrets.yaml` with your actual secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ecommerce-secrets
  namespace: ecommerce-platform
type: Opaque
stringData:
  jwt-secret: "your-jwt-secret-key"
  db-password: "your-db-password"
  redis-password: ""
```

Apply secrets:

```bash
kubectl apply -f k8s/secrets.yaml
```

### Step 3: Create ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

### Step 4: Deploy Database (if needed)

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres \
  -n ecommerce-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis \
  -n ecommerce-platform --timeout=300s
```

### Step 5: Deploy Services

You'll need to create deployment files for each service. Here's an example for `user-service`:

**Create `k8s/user-service-deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: ecommerce-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: ghcr.io/beepeen78/user-service:latest
        ports:
        - containerPort: 3001
        env:
        - name: PORT
          value: "3001"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ecommerce-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: ecommerce-secrets
              key: jwt-secret
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: ecommerce-platform
spec:
  selector:
    app: user-service
  ports:
  - port: 3001
    targetPort: 3001
  type: ClusterIP
```

Deploy each service:

```bash
# Deploy API Gateway
kubectl apply -f k8s/api-gateway-deployment.yaml

# Deploy User Service
kubectl apply -f k8s/user-service-deployment.yaml

# Deploy Product Service
# kubectl apply -f k8s/product-service-deployment.yaml

# ... repeat for other services
```

### Step 6: Deploy API Gateway

```bash
kubectl apply -f k8s/api-gateway-deployment.yaml
```

---

## 🔐 Important: Configure Image Pull Secrets

If using GitHub Container Registry (GHCR), you need to authenticate:

### Step 1: Create Docker Registry Secret

```bash
# Create secret for GHCR
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --namespace=ecommerce

# Or for Docker Hub
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_DOCKERHUB_USERNAME \
  --docker-password=YOUR_DOCKERHUB_PASSWORD \
  --namespace=ecommerce
```

### Step 2: Add to Deployments

Add to each deployment's pod spec:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: ghcr-secret  # or dockerhub-secret
      containers:
      - name: user-service
        # ...
```

---

## 🌐 Set Up Ingress

### Option 1: Using NGINX Ingress Controller

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Wait for controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s
```

Create Ingress resource:

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: ecommerce-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: api.ecommerce.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8080
```

Apply ingress:

```bash
kubectl apply -f k8s/ingress.yaml
```

### Option 2: Using Helm Chart Ingress

The Helm chart includes ingress configuration. Just enable it in `values.yaml`:

```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: api.ecommerce.local
      paths:
        - path: /
          pathType: Prefix
```

---

## ✅ Verification & Testing

### Check Deployment Status

```bash
# Check all resources
kubectl get all -n ecommerce-platform

# Check pods
kubectl get pods -n ecommerce-platform

# Check services
kubectl get svc -n ecommerce-platform

# Check deployments
kubectl get deployments -n ecommerce-platform
```

### View Logs

```bash
# View logs for a specific pod
kubectl logs -f deployment/user-service -n ecommerce-platform

# View logs for all pods in namespace
kubectl logs -f -l app=user-service -n ecommerce-platform

# View logs for API Gateway
kubectl logs -f deployment/api-gateway -n ecommerce-platform
```

### Test Services

```bash
# Port forward to access services
kubectl port-forward svc/api-gateway 8080:8080 -n ecommerce-platform

# Test API Gateway
curl http://localhost:8080/health

# Test User Service directly
kubectl port-forward svc/user-service 3001:3001 -n ecommerce-platform
curl http://localhost:3001/health
```

### Access API Documentation

```bash
# Port forward API Gateway
kubectl port-forward svc/api-gateway 8080:8080 -n ecommerce-platform

# Open browser
# http://localhost:8080/docs
```

---

## 🔄 Update/Upgrade Deployment

### Using Helm

```bash
# Update image tag in values.yaml
# Then upgrade
helm upgrade ecommerce-platform ./helm/ecommerce-platform \
  --namespace ecommerce \
  --reuse-values
```

### Using kubectl

```bash
# Update deployment with new image
kubectl set image deployment/user-service \
  user-service=ghcr.io/beepeen78/user-service:v1.1.0 \
  -n ecommerce-platform

# Or edit deployment directly
kubectl edit deployment/user-service -n ecommerce-platform
```

---

## 🗑️ Cleanup/Uninstall

### Remove Helm Deployment

```bash
helm uninstall ecommerce-platform -n ecommerce
kubectl delete namespace ecommerce
```

### Remove kubectl Resources

```bash
# Delete all resources
kubectl delete -f k8s/

# Delete namespace (removes everything)
kubectl delete namespace ecommerce-platform
```

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n ecommerce-platform

# Check events
kubectl get events -n ecommerce-platform --sort-by='.lastTimestamp'

# Common issues:
# - Image pull errors → Check imagePullSecrets
# - CrashLoopBackOff → Check logs
# - Pending → Check resources/limits
```

### Image Pull Errors

```bash
# Verify image exists
docker pull ghcr.io/beepeen78/user-service:latest

# Check image pull secrets
kubectl get secrets -n ecommerce-platform

# Recreate secret if needed
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  --namespace=ecommerce-platform
```

### Service Connection Issues

```bash
# Test service connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://user-service:3001/health

# Check DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup user-service
```

---

## 📚 Next Steps

1. **Set up monitoring** - Prometheus, Grafana
2. **Configure autoscaling** - HPA (Horizontal Pod Autoscaler)
3. **Add service mesh** - Istio, Linkerd
4. **Set up CI/CD** - Auto-deploy from GitHub
5. **Configure backups** - Database backups

---

## 🔗 Quick Reference

### Essential Commands

```bash
# Deploy with Helm
helm install ecommerce-platform ./helm/ecommerce-platform -n ecommerce --create-namespace

# Check status
kubectl get all -n ecommerce

# View logs
kubectl logs -f deployment/api-gateway -n ecommerce

# Port forward
kubectl port-forward svc/api-gateway 8080:8080 -n ecommerce

# Delete everything
helm uninstall ecommerce-platform -n ecommerce
kubectl delete namespace ecommerce
```

---

**Your application is now deployed to Kubernetes! 🎉**

