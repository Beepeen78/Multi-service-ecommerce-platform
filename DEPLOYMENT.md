# Deployment Guide

This guide covers deployment options for the Multi-Service E-Commerce Platform.

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Kubernetes cluster (for K8s deployment)
- kubectl configured (for K8s deployment)
- Environment variables configured

## Quick Start

### Local Development with Docker Compose

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **View logs:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

4. **Stop services:**
   ```bash
   docker-compose -f docker-compose.dev.yml down
   ```

### Production Deployment with Docker Compose

1. **Set environment variables:**
   ```bash
   export JWT_SECRET=your-secret-key
   export STRIPE_SECRET_KEY=your-stripe-key
   # ... other required variables
   ```

2. **Build and deploy:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Check status:**
   ```bash
   docker-compose ps
   ```

### Kubernetes Deployment

1. **Create namespace:**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   ```

2. **Update secrets:**
   ```bash
   # Edit k8s/secrets.yaml with your actual secrets
   kubectl apply -f k8s/secrets.yaml
   ```

3. **Update ConfigMap if needed:**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   ```

4. **Deploy infrastructure (databases):**
   ```bash
   kubectl apply -f k8s/postgres-deployment.yaml
   kubectl apply -f k8s/redis-deployment.yaml
   ```

5. **Wait for databases to be ready:**
   ```bash
   kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce-platform --timeout=300s
   kubectl wait --for=condition=ready pod -l app=redis -n ecommerce-platform --timeout=300s
   ```

6. **Deploy services:**
   ```bash
   kubectl apply -f k8s/api-gateway-deployment.yaml
   # Deploy other services similarly
   ```

7. **Check deployment status:**
   ```bash
   kubectl get pods -n ecommerce-platform
   kubectl get services -n ecommerce-platform
   ```

## Using Deployment Scripts

### Linux/Mac

```bash
# Development
./scripts/deploy.sh development docker

# Production with Docker Compose
./scripts/deploy.sh production docker

# Production with Kubernetes
./scripts/deploy.sh production kubernetes
```

### Windows PowerShell

```powershell
# Development
.\scripts\deploy.ps1 -Environment development -Method docker

# Production with Docker Compose
.\scripts\deploy.ps1 -Environment production -Method docker

# Production with Kubernetes
.\scripts\deploy.ps1 -Environment production -Method kubernetes
```

## CI/CD with GitHub Actions

The project includes GitHub Actions workflow for automated deployment:

1. **Configure secrets in GitHub:**
   - `KUBE_CONFIG_STAGING` - Base64 encoded kubeconfig for staging
   - `KUBE_CONFIG_PRODUCTION` - Base64 encoded kubeconfig for production
   - Other service-specific secrets

2. **Workflow triggers:**
   - Push to `main/master` → Build and deploy to production
   - Push to `develop` → Build and deploy to staging
   - Pull requests → Build and test only

3. **Image Registry:**
   - Images are pushed to GitHub Container Registry (ghcr.io)
   - Update `REGISTRY` and `IMAGE_PREFIX` in `.github/workflows/deploy.yml` if using different registry

## Service Architecture

### Services

- **API Gateway** (Port 8080) - Entry point for all requests
- **User Service** (Port 3001) - User management and authentication
- **Product Service** (Port 3002) - Product catalog management
- **Order Service** (Port 3003) - Order processing
- **Payment Service** (Port 3004) - Payment processing
- **Inventory Service** (Port 3005) - Inventory management
- **Notification Service** (Port 3006) - Email and push notifications

### Infrastructure

- **PostgreSQL** (Port 5432) - Primary database
- **Redis** (Port 6379) - Caching and session storage
- **Nginx** (Port 80/443) - Load balancer and reverse proxy

## Environment Variables

Required environment variables (see `.env.example`):

- Database: `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Redis: `REDIS_URL`
- JWT: `JWT_SECRET`, `JWT_EXPIRES_IN`
- Payment: `STRIPE_SECRET_KEY`, `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`
- Email: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`

## Scaling

### Docker Compose Scaling

```bash
# Scale a specific service
docker-compose up -d --scale user-service=3

# Scale multiple services
docker-compose up -d --scale user-service=3 --scale product-service=2
```

### Kubernetes Scaling

```bash
# Scale using kubectl
kubectl scale deployment user-service --replicas=3 -n ecommerce-platform

# Or update replicas in deployment YAML and apply
kubectl apply -f k8s/user-service-deployment.yaml
```

## Health Checks

All services should implement `/health` endpoint for monitoring:

```bash
# Check API Gateway health
curl http://localhost:8080/health

# Check service health in Kubernetes
kubectl get pods -n ecommerce-platform
kubectl describe pod <pod-name> -n ecommerce-platform
```

## Monitoring and Logs

### Docker Compose

```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api-gateway

# View resource usage
docker stats
```

### Kubernetes

```bash
# View logs
kubectl logs -f deployment/api-gateway -n ecommerce-platform

# View logs from all pods in a service
kubectl logs -f -l app=api-gateway -n ecommerce-platform

# Describe resources
kubectl describe deployment api-gateway -n ecommerce-platform
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Check if ports are already in use: `netstat -an | grep <port>`
   - Update ports in docker-compose.yml or service configurations

2. **Database connection issues:**
   - Verify database is running: `docker-compose ps postgres`
   - Check connection string in environment variables
   - Ensure database is initialized: `docker-compose exec postgres psql -U user -d ecommerce`

3. **Service not starting:**
   - Check logs: `docker-compose logs <service-name>`
   - Verify environment variables are set correctly
   - Check resource limits (memory/CPU)

4. **Kubernetes deployment issues:**
   - Check pod status: `kubectl get pods -n ecommerce-platform`
   - Describe pod for events: `kubectl describe pod <pod-name> -n ecommerce-platform`
   - Check service endpoints: `kubectl get endpoints -n ecommerce-platform`

## Security Considerations

1. **Secrets Management:**
   - Never commit secrets to version control
   - Use Kubernetes Secrets or external secret management (HashiCorp Vault, AWS Secrets Manager)
   - Rotate secrets regularly

2. **Network Security:**
   - Use internal networks for service-to-service communication
   - Expose only necessary ports
   - Implement proper firewall rules

3. **SSL/TLS:**
   - Configure SSL certificates for production
   - Use Let's Encrypt or your CA for certificates
   - Update nginx.conf with SSL configuration

4. **Access Control:**
   - Implement proper authentication and authorization
   - Use RBAC in Kubernetes
   - Limit container capabilities

## Backup and Recovery

### Database Backups

```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U user ecommerce > backup.sql

# Restore
docker-compose exec -T postgres psql -U user ecommerce < backup.sql
```

### Persistent Volumes (Kubernetes)

- Ensure PersistentVolumeClaims are properly configured
- Implement regular backups of persistent volumes
- Test restore procedures regularly

## Rollback Procedures

### Docker Compose

```bash
# Stop current deployment
docker-compose down

# Deploy previous version
docker-compose up -d
```

### Kubernetes

```bash
# Rollback deployment
kubectl rollout undo deployment/api-gateway -n ecommerce-platform

# Check rollout history
kubectl rollout history deployment/api-gateway -n ecommerce-platform

# Rollback to specific revision
kubectl rollout undo deployment/api-gateway --to-revision=2 -n ecommerce-platform
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

