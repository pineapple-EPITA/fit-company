# ADR 02: Coach Service Migration

## Context
Our WOD (Workout of the Day) feature is struggling with performance as we grow. Users are waiting up to 5 seconds for their workouts, which is way too long. We need to do something about this before it starts hurting our user experience.

## Decision
After some back-and-forth with the team, we decided to break out the WOD generation into its own service. We're going with the Strangler Fig pattern because:
1. It lets us move fast without breaking things
2. We can scale the workout generation separately from the main app
3. If something goes wrong, we can easily roll back
4. The team can work on workout features without touching the monolith

## Implementation Steps

1. **Phase 1: Getting Ready (Current)**
   - Separate the new coach service with Flask (the logic is used to be in the fit/services/fitness_coach.py)
   - Add health checks and monitoring
   - Set up Docker stuff
   - Test it locally with docker-compose

2. **Phase 2: The Switch**
   - Update nginx to send /fitness/wod to the new service
   - Keep the old code running as backup
   - Watch the metrics like a hawk

3. **Phase 3: Moving Traffic**
   - Start with 10% of traffic
   - If it looks good, bump it up slowly
   - Keep the old endpoint ready just in case

4. **Phase 4: Cleanup**
   - Once we're confident, we will remove the old code
   - Update docs
   - Clean up the nginx config

## Technical approaches

### API Design
We kept the API simple with a single endpoint for WOD generation. Here's what we're using:

1. The endpoint in `src/coach_microservice/app.py`:
```python
@app.route("/fitness/wod", methods=["GET"])
@jwt_required()
def get_wod():
    # Returns a WodResponseSchema containing:
    # - List of exercises with muscle group impacts
    # - Generation timestamp
```

2. The data models in `src/coach_microservice/schema/dto.py`:
```python
class WodResponseSchema:
    exercises: List[WodExerciseSchema]
    generated_at: datetime

class WodExerciseSchema:
    id: int
    name: str
    description: str
    difficulty: int  # 1-5 scale
    muscle_groups: List[MuscleGroupImpact]
    suggested_weight: float
    suggested_reps: int

class MuscleGroupImpact:
    id: int
    name: str
    body_part: str
    is_primary: bool
    intensity: float  # 0.0 to 1.0
```

We chose this design because:
- Single responsibility: just handles WOD generation
- Stateless: gets user history from monolith when needed
- Simple data model: easy to understand and maintain
- JWT auth: secure and stateless

### Service Communication
- Coach service makes HTTP calls to monolith to get user's exercise history
- JWT tokens are used for authentication between services
- Nginx handles routing and load balancing
- Services communicate synchronously to maintain consistency

### Why Nginx?
We're using Nginx as our reverse proxy because:
- It's battle-tested and super fast
- Handles load balancing out of the box (crucial for scaling the coach service)
- Makes the strangler fig pattern easy - just update the routing rules
- Takes care of SSL/TLS termination

### How It Works
The Coach microservice is a Flask app secured with JWT authentication.

No DB. Instead, it communicates with the monolith service via HTTP to:

- Fetch the full list of available exercises

- Fetch the user's recent workout history, specifically the exercises completed yesterday

Once it has the data, the coach service:

- Filters out any exercises the user completed yesterday

- Randomly selects 6 non-repeating exercises from the remaining exercises

- The final list of selected exercises is returned in a structured JSON response, along with the generation timestamp.
- Docker for easy deployment
- Nginx in front for routing

### What we're aiming for
- Response time under 5s for 95% of requests
- Less than 1% or zero errors :)
- Handle 100 users at once without breaking a sweat

### Monitoring
- Health check endpoint (/health)
- Response time tracking
- Error counting
- Load testing with k6

## Status
Working on Phase 1 - got the basic service running, now adding tests

## Consequences

### The Good
- Better performance
- Easier to scale
- Can deploy workout changes without touching the main app
- Simpler to maintain

### The Bad
- More moving parts
- Need to coordinate between services
- Costs a bit more to run

### Our safety nets
- Good monitoring
- Easy rollback if needed
- Taking it slow with the migration
- Lots of testing before each step