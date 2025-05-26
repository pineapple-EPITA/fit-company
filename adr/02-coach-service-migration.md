# ADR 02: Strangler Fig Proxy Setup for Coach Service Migration

## Status
Accepted

## Context
The monolith application is being migrated to a microservices architecture. To ensure zero downtime and a smooth transition, a Strangler Fig pattern is being implemented using a reverse proxy (Nginx).

## Decision
We've chosen Nginx to act as our "strangler fig" proxy. Initially, all incoming traffic, especially to our /api/wod endpoints, will continue to go to our existing monolith. The Nginx setup makes it super easy to redirect this traffic to our new "Coach" microservice as soon as it's ready.

## Consequences
- **Zero Downtime**: The proxy allows us to gradually shift traffic without disrupting users.
- **Flexibility**: The Nginx configuration can be updated to route specific endpoints to the new microservice as it becomes available.
- **Simplicity**: Using Nginx as a reverse proxy is a well-established pattern, making it easy to maintain and extend. 

## Reasoning
- **Clearer Architecture**: By separating the "Workout of the Day" (WOD) logic into its own "Coach" service, we're building a much cleaner and more organized system.
- **Independent Development**: The Coach service can be developed, tested, and scaled on its own without affecting the monolith. This means faster development cycles and fewer headaches.
- **Ready for the Future**: This migration isn't just about the Coach service; it's setting the stage for a fully microservices-based platform.

## Migration Strategy
- **Starting**: Right now, all traffic still goes to the monolith.
- **Gradual Shift**: We'll configure the proxy to send specific traffic (like internal requests or tests from our team) to the new Coach service first.
- **Testing**: We'll use our K6 script (tests/load/load-test-k6.js) to rigorously test the system under expected user loads.
- **Traffic**: Once we're confident, we'll slowly increase the percentage of live user traffic routed to the Coach service, always keeping a close eye on performance and stability.
- **Finalize**: Once we've validated everything, we'll make the full switch!

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