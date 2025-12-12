# Deployment Guide

## Prerequisites

1. Kubernetes cluster (v1.24+)
2. kubectl configured
3. Helm 3.x
4. Istio 1.17+ (for service mesh)
5. Docker (for building images)

## Step 1: Install Infrastructure Components

### Install Ingress-NGINX
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### Install Cert-Manager (for TLS)
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

Wait for cert-manager to be ready:
```bash
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
```

Apply ClusterIssuer:
```bash
kubectl apply -f k8s/cert-manager/cluster-issuer.yaml
```

### Install Prometheus Stack
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f monitoring/prometheus-values.yaml
```

### Install Loki Stack
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace monitoring \
  -f logging/loki-values.yaml
```

### Install KEDA
```bash
helm repo add kedacore https://kedacore.github.io/charts
helm install keda kedacore/keda \
  --namespace keda \
  --create-namespace
```

### Install Istio
```bash
istioctl install --set values.defaultRevision=default -y
kubectl label namespace ecommerce istio-injection=enabled
```

## Step 2: Deploy Application

### Option A: Deploy with Helm
```bash
# Build and push images first
make build

# Deploy
cd helm/ecommerce-platform
helm dependency update
helm install ecommerce-platform . \
  --namespace ecommerce \
  --create-namespace \
  --wait \
  --timeout 10m
```

### Option B: Deploy with ArgoCD (GitOps)

1. Install ArgoCD:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

2. Get ArgoCD admin password:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

3. Port-forward ArgoCD UI:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

4. Apply ArgoCD applications:
```bash
kubectl apply -f argocd/applications/ecommerce-platform.yaml
```

## Step 3: Initialize Database

```bash
kubectl apply -f k8s/database/init-job.yaml
kubectl wait --for=condition=complete job/db-init -n ecommerce --timeout=300s
```

## Step 4: Configure Canary Deployments (Optional)

```bash
kubectl apply -f istio/canary/virtual-service.yaml
kubectl apply -f istio/canary/product-service-canary.yaml
```

## Step 5: Verify Deployment

```bash
# Check all pods
kubectl get pods -n ecommerce

# Check services
kubectl get svc -n ecommerce

# Check ingress
kubectl get ingress -n ecommerce

# Check HPA
kubectl get hpa -n ecommerce

# Check KEDA scaled objects
kubectl get scaledobjects -n ecommerce
```

## Accessing Services

### API Endpoints
- Auth Service: `https://api.ecommerce.local/api/auth/*`
- User Service: `https://api.ecommerce.local/api/users/*`
- Product Service: `https://api.ecommerce.local/api/products/*`
- Cart Service: `https://api.ecommerce.local/api/cart/*`
- Order Service: `https://api.ecommerce.local/api/orders/*`
- Payment Service: `https://api.ecommerce.local/api/payments/*`

### Monitoring
- Grafana: `http://grafana.monitoring.local` (admin/admin)
- Prometheus: `http://prometheus.monitoring.local`
- Loki: `http://loki.monitoring.local`

## Scaling

### Manual Scaling
```bash
kubectl scale deployment product-service -n ecommerce --replicas=5
```

### HPA (Automatic)
HPA is configured automatically via Helm values. Adjust in `helm/ecommerce-platform/values.yaml`.

### KEDA (Event-driven)
KEDA is configured for order-service based on Kafka lag. Adjust in Helm values.

## Troubleshooting

### View logs
```bash
kubectl logs -f deployment/product-service -n ecommerce
```

### Check events
```bash
kubectl get events -n ecommerce --sort-by='.lastTimestamp'
```

### Debug pod
```bash
kubectl exec -it deployment/product-service -n ecommerce -- /bin/sh
```

### Check resource usage
```bash
kubectl top pods -n ecommerce
kubectl top nodes
```

