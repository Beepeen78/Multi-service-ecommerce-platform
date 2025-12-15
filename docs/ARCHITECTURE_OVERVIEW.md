# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Client / User                                  │
└──────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ HTTPS/TLS
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Ingress-NGINX (TLS Termination)                      │
│                    cert-manager (Let's Encrypt)                          │
└──────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ Internal Routing
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Istio Service Mesh                              │
│                    (Traffic Management & Canary)                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Auth Service     │ │ User Service │ │Product Service│
    │  (Node.js)        │ │    (Go)      │ │  (Node.js)    │
    └─────────┬─────────┘ └──────┬───────┘ └──────┬───────┘
              │                   │                │
              ▼                   ▼                ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Cart Service    │ │Order Service │ │Payment Service│
    │  (Node.js)       │ │    (Go)      │ │  (Node.js)    │
    └─────────┬────────┘ └──────┬───────┘ └──────┬───────┘
              │                   │                │
              ▼                   ▼                ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │Inventory Service │ │Notification  │ │Recommendation│
    │   (Python)       │ │   Service    │ │   Service    │
    │                  │ │  (Python)    │ │  (Python)    │
    └──────────────────┘ └──────────────┘ └──────────────┘
              │                   │                │
              └───────────────────┼────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
        ┌──────────────┐ ┌──────────┐ ┌──────────────┐
        │  PostgreSQL  │ │  Redis   │ │    Kafka     │
        │  (Primary DB)│ │ (Cache)   │ │  (Events)    │
        └──────────────┘ └──────────┘ └──────────────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌──────────────────────┐   ┌──────────────────────┐
        │   Prometheus         │   │      Loki             │
        │   (Metrics)          │   │   (Logs)              │
        └──────────────────────┘   └──────────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │     Grafana      │
                        │  (Visualization) │
                        └──────────────────┘
```

## Request Flow Example: Order Processing

### 1. User Request Flow
```
User → Ingress-NGINX → Istio → Auth Service → User Service
```

### 2. Order Creation Flow
```
1. User → Ingress → Cart Service (GET /api/cart/:userId)
   └─→ Redis (retrieve cart items)

2. User → Ingress → Order Service (POST /api/orders)
   ├─→ PostgreSQL (create order record)
   ├─→ Inventory Service (reserve inventory)
   │   └─→ PostgreSQL (update inventory)
   └─→ Kafka (publish order.created event)

3. Kafka Event → Notification Service (consumer)
   ├─→ PostgreSQL (store notification)
   └─→ Redis (cache notification)

4. User → Ingress → Payment Service (POST /api/payments)
   ├─→ PostgreSQL (create payment record)
   └─→ Redis (cache payment status)

5. User → Ingress → Notification Service (GET /api/notifications/:userId)
   └─→ Redis (retrieve cached notifications) or PostgreSQL (fallback)
```

### 3. Data Flow Architecture

**Synchronous (REST):**
- Client ↔ Ingress ↔ Service ↔ Database
- Service ↔ Service (direct HTTP calls)

**Asynchronous (Events):**
- Service → Kafka → Consumer Service
- Order Service publishes events → Notification Service consumes

**Caching Layer:**
- Service → Redis (read cache)
- Service → PostgreSQL (write-through)

## Technology Stack by Layer

### Edge Layer
- **Ingress-NGINX**: Load balancing, SSL termination, routing
- **cert-manager**: Automated TLS certificate management
- **Istio**: Service mesh, traffic management, canary deployments

### Application Layer (Microservices)
- **Node.js Services**: Express.js, REST APIs, JWT authentication
- **Go Services**: High-performance services, Kafka integration
- **Python Services**: Flask, event consumers, ML recommendations

### Data Layer
- **PostgreSQL**: Primary database, ACID transactions
- **Redis**: Caching, session storage, cart management
- **Kafka**: Event streaming, async communication

### Observability Layer
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Loki + Promtail**: Centralized logging

### Infrastructure Layer
- **Kubernetes**: Container orchestration
- **Helm**: Package management
- **HPA**: Horizontal pod autoscaling
- **KEDA**: Event-driven autoscaling
- **ArgoCD**: GitOps deployment

## Service Communication Patterns

### Synchronous Communication
- **REST APIs**: Service-to-service HTTP calls
- **gRPC**: (Can be extended for internal communication)

### Asynchronous Communication
- **Kafka Topics**: 
  - `orders`: Order lifecycle events
  - `notifications`: Notification events
  - `inventory`: Inventory update events

### Caching Strategy
- **Read-through**: Check Redis first, fallback to PostgreSQL
- **Write-through**: Write to PostgreSQL, update Redis
- **TTL-based**: Automatic cache expiration (5-60 minutes)

## Scalability Patterns

### Horizontal Scaling
- **HPA**: CPU/Memory-based (70% CPU, 80% Memory thresholds)
- **KEDA**: Kafka lag-based (10 message threshold)

### Load Distribution
- **Round-robin**: Kubernetes service load balancing
- **Istio**: Advanced traffic splitting for canary deployments

## Security Layers

1. **TLS/SSL**: All external traffic encrypted
2. **JWT Tokens**: Authentication and authorization
3. **Service Mesh**: mTLS for internal communication
4. **Network Policies**: (Can be added for pod-to-pod security)

