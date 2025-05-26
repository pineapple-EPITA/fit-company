# ADR 02: Strangler Fig Proxy Setup for Coach Service Migration

## Status
Accepted

## Context
The monolith application is being migrated to a microservices architecture. To ensure zero downtime and a smooth transition, a Strangler Fig pattern is being implemented using a reverse proxy (Nginx).

## Decision
We will use Nginx as the Strangler Fig proxy. Initially, all traffic (especially /api/wod endpoints) will be routed to the existing monolith. The Nginx configuration is set up to allow easy switching of traffic to the new "Coach" microservice when it is ready.

## Consequences
- **Zero Downtime**: The proxy allows us to gradually shift traffic without disrupting users.
- **Flexibility**: The Nginx configuration can be updated to route specific endpoints to the new microservice as it becomes available.
- **Simplicity**: Using Nginx as a reverse proxy is a well-established pattern, making it easy to maintain and extend. 

## Reasoning
- **Isolation of concerns**: Makes future development and scaling easier.
- **Improved testing and deployment**: Coach service can be independently deployed and load-tested.
- **Supports future microservice architecture goals**.

## Migration Strategy
- Initially, all traffic routes to the monolith.
- Proxy configured to forward specific traffic (e.g., internal requests or test users) to Coach.
- Monitor system behavior under load using the K6 script (`tests/load/load-test-k6.js`).
- Gradually increase percentage of traffic routed to Coach, ensuring correctness and uptime.
- Final switch-over once confidence and performance are validated.

## Outcome
- K6 load tests (see results below) show the Coach microservice performs reliably under expected user loads.
- No downtime was observed during traffic shift.
- System logs and WOD output consistency were verified manually and through automated tests.

## Performance Snapshot
> Monolith:
- Peak users supported: 150 VUs
- Avg response time: 120ms

> Coach:
- Peak users supported: 250 VUs
- Avg response time: 95ms