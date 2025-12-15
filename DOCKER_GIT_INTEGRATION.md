# Connecting Git Repository to Docker

This guide explains how your Git repository is connected to Docker and how to set up automated Docker builds.

---

## 🔗 Current Integration

Your repository is already connected to Docker through:

1. **Docker Compose** - `docker-compose.yml` defines all services
2. **Dockerfiles** - Each service has its own `Dockerfile`
3. **GitHub Actions** - Automated builds and pushes (when configured)

---

## 📋 How It Works

### 1. Local Development Flow

```bash
# Clone repository
git clone https://github.com/Beepeen78/Multi-service-ecommerce-platform.git
cd Multi-service-ecommerce-platform

# Build and start all services
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Docker Compose Structure

Your `docker-compose.yml` builds images from your Git repository:

```yaml
services:
  api-gateway:
    build:
      context: ./services/api-gateway  # Builds from this directory
      dockerfile: Dockerfile           # Uses Dockerfile in this directory
    # ... configuration
```

Each service directory contains:
- `main.py` - Python/FastAPI application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker build instructions

---

## 🚀 Setting Up Automated Docker Builds

### Option 1: GitHub Container Registry (GHCR) - Recommended

**Already configured in `.github/workflows/docker-build.yml`**

#### Steps:

1. **Enable GitHub Actions** (if not already enabled)
   - Go to your repository → Settings → Actions → General
   - Enable "Allow all actions and reusable workflows"

2. **Push to GitHub**
   ```bash
   git add .github/workflows/docker-build.yml
   git commit -m "Add Docker build workflow"
   git push origin main
   ```

3. **View built images**
   - Go to your repository → Packages
   - Images will be at: `ghcr.io/beepeen78/<service-name>`

4. **Pull images**
   ```bash
   docker pull ghcr.io/beepeen78/api-gateway:latest
   ```

### Option 2: Docker Hub

#### Setup:

1. **Create Docker Hub account** (if you don't have one)
   - Go to https://hub.docker.com

2. **Add Docker Hub secrets to GitHub**
   - Go to repository → Settings → Secrets and variables → Actions
   - Add secrets:
     - `DOCKERHUB_USERNAME` - Your Docker Hub username
     - `DOCKERHUB_TOKEN` - Your Docker Hub access token

3. **Update GitHub Actions workflow** to use Docker Hub:

```yaml
env:
  REGISTRY: docker.io
  IMAGE_PREFIX: YOUR_DOCKERHUB_USERNAME

steps:
  - name: Log in to Docker Hub
    uses: docker/login-action@v3
    with:
      username: ${{ secrets.DOCKERHUB_USERNAME }}
      password: ${{ secrets.DOCKERHUB_TOKEN }}
```

---

## 🔄 Workflow Overview

### When you push to GitHub:

```
Git Push (main branch)
    ↓
GitHub Actions Triggered
    ↓
Build Docker Images (for each service)
    ↓
Push to Container Registry (GHCR/Docker Hub)
    ↓
Images available for deployment
```

### Service Build Process:

For each service (api-gateway, user-service, etc.):
1. Checkout code from Git
2. Build Docker image using Dockerfile
3. Tag image with version/branch/sha
4. Push to container registry

---

## 📦 Using Built Images

### Update docker-compose.yml to use pre-built images:

Instead of building locally, you can use images from the registry:

```yaml
services:
  api-gateway:
    image: ghcr.io/beepeen78/api-gateway:latest
    # Remove build section if using pre-built image
    ports:
      - "8080:8080"
    # ... rest of config
```

### Pull and run:

```bash
# Pull latest images
docker-compose pull

# Run with pre-built images
docker-compose up -d
```

---

## 🛠️ Manual Docker Operations

### Build specific service:

```bash
# Build api-gateway
docker build -t api-gateway:latest ./services/api-gateway

# Build all services
docker-compose build
```

### Tag and push manually:

```bash
# Tag image
docker tag api-gateway:latest ghcr.io/beepeen78/api-gateway:v1.0.0

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push
docker push ghcr.io/beepeen78/api-gateway:v1.0.0
```

---

## 🔐 Container Registry Access

### GitHub Container Registry (GHCR)

**Public repositories:**
- Images are public by default
- No authentication needed to pull

**Private repositories:**
```bash
# Login with GitHub Personal Access Token
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull private image
docker pull ghcr.io/beepeen78/private-service:latest
```

### Docker Hub

```bash
# Login
docker login

# Pull public image
docker pull username/service-name:latest
```

---

## 📊 Image Tags Strategy

The workflow automatically creates tags:

- `latest` - Latest build from main branch
- `main-<sha>` - Specific commit from main branch
- `v1.0.0` - Semantic version (when you create a git tag)
- `pr-123` - Pull request builds

---

## 🎯 Best Practices

1. **Use specific tags in production**
   ```yaml
   image: ghcr.io/beepeen78/api-gateway:v1.0.0  # ✅ Specific version
   # Not: image: ghcr.io/beepeen78/api-gateway:latest  # ❌ Can change
   ```

2. **Enable image scanning**
   - GitHub automatically scans images for vulnerabilities
   - View in: Packages → Your Package → Security

3. **Use multi-stage builds** (already in your Dockerfiles)
   - Reduces final image size
   - Faster builds with layer caching

4. **Tag releases**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

---

## 🔍 Monitoring Builds

### View build status:
- GitHub repository → Actions tab
- See which services built successfully
- View build logs for debugging

### View published images:
- GitHub repository → Packages tab
- See all versions/tags
- Download or view image details

---

## 🚨 Troubleshooting

### Build fails in GitHub Actions:

1. **Check Dockerfile syntax**
   ```bash
   docker build -t test ./services/api-gateway
   ```

2. **Check Python dependencies**
   - Ensure `requirements.txt` is correct
   - Test locally first

3. **Check build logs**
   - GitHub Actions → Failed workflow → Build job → Service step

### Images not appearing:

1. **Check permissions**
   - Ensure GitHub Actions has write access to packages
   - Repository Settings → Actions → General → Workflow permissions

2. **Check workflow file**
   - Ensure `.github/workflows/docker-build.yml` is committed
   - Check YAML syntax

---

## 📚 Additional Resources

- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

**Your repository is now set up for automated Docker builds! 🎉**

