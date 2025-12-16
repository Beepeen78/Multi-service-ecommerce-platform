# Complete CI/CD Setup Guide

This guide explains how to set up full CI/CD (Continuous Integration and Continuous Deployment) for your e-commerce platform.

---

## 🎯 What is CI/CD?

### CI (Continuous Integration)
- ✅ **Automatically builds** your code on every push
- ✅ **Runs tests** to catch errors early
- ✅ **Builds Docker images** for all services

### CD (Continuous Deployment)
- ✅ **Pushes images** to container registry
- ✅ **Automatically deploys** to staging/production
- ✅ **Rolls back** if deployment fails

---

## 📋 Current Setup

Your repository has multiple CI/CD workflows:

### 1. `docker-build.yml` (Currently Active)
- **CI**: ✅ Builds Docker images
- **CD**: ⚠️ Only pushes images (no deployment)

### 2. `ci-cd-complete.yml` (New - Full CI/CD)
- **CI**: ✅ Builds, tests, and creates images
- **CD**: ✅ Pushes images AND deploys (when configured)

---

## 🚀 How to Activate Full CI/CD

### Option 1: Keep Current Setup (Images Only)

**What you have now:**
- Builds Docker images on push
- Pushes to GitHub Container Registry
- No automatic deployment (manual deployment required)

**Good for:**
- Development/testing
- When you deploy manually
- Learning CI/CD basics

### Option 2: Full CI/CD (Recommended)

**What you get:**
- Everything in Option 1, PLUS
- Automatic deployment to Kubernetes
- Staging environment on `develop` branch
- Production environment on `main` branch

**Requires:**
1. Kubernetes cluster access
2. Helm installed
3. GitHub secrets configured

---

## 📝 Step-by-Step Setup

### Step 1: Enable the Complete CI/CD Workflow

The new workflow (`ci-cd-complete.yml`) is ready but needs activation:

```bash
# Option A: Rename to make it primary
git mv .github/workflows/docker-build.yml .github/workflows/docker-build-backup.yml
git mv .github/workflows/ci-cd-complete.yml .github/workflows/ci-cd.yml

# Option B: Keep both (different names)
# ci-cd-complete.yml will run automatically
```

### Step 2: Configure Kubernetes Deployment (Optional)

If you want automatic deployment:

#### A. Get Kubernetes Config

```bash
# For your Kubernetes cluster
kubectl config view --flatten > kubeconfig-staging.yaml
kubectl config view --flatten > kubeconfig-production.yaml
```

#### B. Add Secrets to GitHub

1. Go to: `Settings` → `Secrets and variables` → `Actions`
2. Add these secrets:

**For Staging:**
- Name: `KUBE_CONFIG_STAGING`
- Value: Base64 encoded kubeconfig
  ```bash
  cat kubeconfig-staging.yaml | base64
  ```

**For Production:**
- Name: `KUBE_CONFIG_PRODUCTION`
- Value: Base64 encoded kubeconfig
  ```bash
  cat kubeconfig-production.yaml | base64
  ```

#### C. Install Helm (if not already installed)

The workflow uses Helm for deployments. Ensure your Kubernetes cluster has Helm charts ready.

---

## 🔄 Workflow Behavior

### On Pull Request:
```
PR Created
  ↓
✅ CI: Build & Test
✅ CI: Build Docker Images
❌ CD: Images NOT pushed (saves registry space)
❌ CD: No deployment
```

### On Push to `develop` branch:
```
Code Pushed to develop
  ↓
✅ CI: Build & Test
✅ CD: Build & Push Images (tagged as 'develop')
✅ CD: Deploy to Staging (if KUBE_CONFIG_STAGING configured)
```

### On Push to `main` branch:
```
Code Pushed to main
  ↓
✅ CI: Build & Test
✅ CD: Build & Push Images (tagged as 'latest')
✅ CD: Deploy to Production (if KUBE_CONFIG_PRODUCTION configured)
```

### On Git Tag (e.g., v1.0.0):
```
Tag Created
  ↓
✅ CI: Build & Test
✅ CD: Build & Push Images (tagged as 'v1.0.0')
❌ CD: No automatic deployment (manual approval recommended)
```

---

## 🎛️ Service Matrix

The workflow builds **all 10 services**:

**Python/FastAPI (8 services):**
- api-gateway
- user-service
- product-service
- order-service
- payment-service
- inventory-service
- notification-service
- recommendation-service

**Node.js (2 services):**
- auth-service
- cart-service

---

## 📊 Monitoring CI/CD

### View Build Status:
- **GitHub Actions**: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
- See which services built successfully
- Check test results
- View deployment logs

### View Published Images:
- **GitHub Packages**: https://github.com/YOUR_USERNAME/YOUR_REPO/pkgs
- All versions/tags
- Image size and pull commands

### View Deployments:
- **Kubernetes Dashboard** (if installed)
- Or via `kubectl get deployments -n ecommerce`

---

## 🔧 Troubleshooting

### Images Not Building

**Check:**
1. Dockerfile exists in service directory
2. GitHub Actions permissions enabled
3. Workflow file syntax is correct

**Fix:**
```bash
# Test locally first
docker build -t test ./services/api-gateway
```

### Deployment Failing

**Check:**
1. `KUBE_CONFIG_STAGING` or `KUBE_CONFIG_PRODUCTION` secrets set
2. Kubernetes cluster is accessible
3. Helm charts are correct

**Fix:**
```bash
# Test deployment manually
kubectl apply -f k8s/
helm upgrade --install ecommerce ./helm/ecommerce-platform
```

### Tests Failing

**Check:**
1. Test files exist
2. Dependencies installed correctly
3. Test environment configured

**Fix:**
```bash
# Run tests locally
cd services/user-service
pip install -r requirements.txt
pytest .  # or npm test for Node.js
```

---

## 🎯 Best Practices

### 1. Use Semantic Versioning
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 2. Test Before Production
- Use `develop` branch for staging
- Test thoroughly in staging
- Only merge to `main` when ready

### 3. Monitor Deployments
- Check GitHub Actions logs
- Monitor Kubernetes pods
- Set up alerts for failures

### 4. Rollback Strategy
```bash
# If deployment fails, rollback with Helm
helm rollback ecommerce-platform -n ecommerce
```

---

## 📚 Next Steps

1. **Review** the `ci-cd-complete.yml` workflow
2. **Choose** your deployment strategy:
   - Images only (current setup) ✅
   - Full CI/CD with Kubernetes (requires setup)
3. **Configure** secrets if deploying to Kubernetes
4. **Test** with a small change and push
5. **Monitor** the first deployment

---

## 🔗 Related Documentation

- [Docker-Git Integration Guide](./DOCKER_GIT_INTEGRATION.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Helm Charts](./helm/ecommerce-platform/README.md)

---

**Your CI/CD pipeline is ready! 🚀**

