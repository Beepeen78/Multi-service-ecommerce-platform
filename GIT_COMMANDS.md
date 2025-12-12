# Git Commands for This Project

## Initial Setup (if needed)

```bash
# Initialize git (if not already done)
git init

# Add remote (if not already configured)
git remote add origin https://github.com/Beepeen78/Multi-service-ecommerce-platform.git
```

## Standard Workflow

### 1. Check Status
```bash
git status
```

### 2. Add All Files
```bash
# Add all files
git add .

# Or add specific files/directories
git add services/
git add helm/
git add README.md
```

### 3. Commit Changes
```bash
git commit -m "feat: add multi-service e-commerce platform with Kubernetes deployment"
```

### 4. Push to Remote
```bash
# Push to main branch
git push origin main

# Or if you're on a different branch
git push origin <branch-name>
```

## Complete Command Sequence

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "feat: implement complete e-commerce platform

- Add 9 microservices (auth, user, product, inventory, cart, order, payment, notification, recommendation)
- Add Helm charts for Kubernetes deployment
- Configure Ingress-NGINX with TLS
- Set up HPA, Prometheus, Grafana, Loki, KEDA
- Add CI/CD with GitHub Actions and ArgoCD
- Configure Istio for canary deployments
- Add comprehensive documentation and testing"

# Push to remote
git push origin main
```

## Alternative: Push with Tags

```bash
# After committing
git tag -a v1.0.0 -m "Initial release: Multi-service e-commerce platform"
git push origin main
git push origin v1.0.0
```

## If You Need to Force Push (use with caution!)

```bash
# Only if you're sure you want to overwrite remote
git push --force origin main
```

## Create a New Branch for Features

```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Make changes, then:
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

