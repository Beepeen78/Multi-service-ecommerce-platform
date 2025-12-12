# Documentation

This directory contains detailed documentation for the e-commerce platform.

## Files

- **ARCHITECTURE_OVERVIEW.md** - Visual architecture diagrams and request flow documentation
  - System architecture diagram (ASCII)
  - Request flow examples
  - Service communication patterns
  - Technology stack by layer

## Architecture Diagram

For a visual representation of the system architecture, see [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md).

The architecture diagram shows:
- Client to Ingress flow
- Service mesh layer
- All 9 microservices
- Data layer (PostgreSQL, Redis, Kafka)
- Observability layer (Prometheus, Loki, Grafana)

## Request Flow

Detailed request flow examples are documented in [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md), including:
- User authentication flow
- Order creation flow
- Event-driven notification flow
- Caching strategies

