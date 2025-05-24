# ADR 02: Strangler Fig Proxy Setup for Coach Service Migration

## Context
The monolith application is being migrated to a microservices architecture. To ensure zero downtime and a smooth transition, a Strangler Fig pattern is being implemented using a reverse proxy (Nginx).

## Decision
We will use Nginx as the Strangler Fig proxy. Initially, all traffic (especially /api/wod endpoints) will be routed to the existing monolith. The Nginx configuration is set up to allow easy switching of traffic to the new "Coach" microservice when it is ready.

## Consequences
- **Zero Downtime**: The proxy allows us to gradually shift traffic without disrupting users.
- **Flexibility**: The Nginx configuration can be updated to route specific endpoints to the new microservice as it becomes available.
- **Simplicity**: Using Nginx as a reverse proxy is a well-established pattern, making it easy to maintain and extend. 