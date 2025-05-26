# ADR 02: Coach Service Migration

## Context
The WOD (Workout of the Day) generation feature is currently part of the monolith application and is experiencing performance issues under load. The service takes up to 5 seconds to generate a response, which is affecting user experience as our user base grows.

## Decision
We will extract the WOD generation functionality into a separate microservice using the Strangler Fig pattern. This will allow us to:
1. Scale the WOD generation independently
2. Optimize the service for performance
3. Reduce load on the main application
4. Enable future enhancements without affecting the monolith

## Implementation Steps

1. **Phase 1: Preparation**
   - Create new coach microservice with WOD generation logic
   - Implement health check endpoint
   - Set up Docker configuration
   - Add service to docker-compose.yml

2. **Phase 2: Strangler Fig Implementation**
   - Update nginx configuration to route /fitness/wod to the new service
   - Keep the old endpoint in the monolith for fallback
   - Monitor performance and error rates

3. **Phase 3: Migration**
   - Gradually increase traffic to the new service
   - Monitor performance metrics
   - Keep the old endpoint as fallback

4. **Phase 4: Cleanup**
   - Remove WOD generation code from monolith
   - Update documentation
   - Remove fallback routing

## Technical Details

### Service Architecture
- Flask-based microservice
- JWT authentication
- No direct database access (stateless)
- Docker containerization
- Nginx reverse proxy

### Performance Targets
- 95th percentile response time < 5s
- Error rate < 1%
- Support for 100 concurrent users

### Monitoring
- Health check endpoint
- Response time metrics
- Error rate tracking
- Load testing with k6

## Status
In Progress - Phase 1

## Consequences

### Positive
- Improved scalability
- Better performance
- Independent deployment
- Easier maintenance

### Negative
- Increased system complexity
- Need for service coordination
- Additional infrastructure costs

### Mitigations
- Comprehensive monitoring
- Fallback mechanisms
- Gradual migration
- Load testing