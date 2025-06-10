# ADR 03: Queue-Based WOD Creation System
---

## Context

The assignment required that the Coach service receives messages to generate WODs (Workout of the Day) for users using a queue system. Messages may randomly fail and should be retried.

However, several additional decisions were made to make the system robuster.

## Status
Accepted

## Decisions

### 1. Logging for debugging

Beside implementing the queue and WOD Generation logic, we added logging to trace actions especially when debugging message loss or retry issues.

```python
logging.info(f"[Consumer] Received message: {body}")
logging.info(f"[Consumer] Error processing message: {str(e)}")
logging.info("[RabbitMQ] Message sent")
```

### 2. Add WOD model to store WOD data of users

To be able to store the generated wod, we implemented 2 tables inside the database of coach service for better data validation, retrieval, and debugging.

```python
class WodModel(Base):
    __tablename__ = "wods"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    exercises = relationship("WodExerciseModel", back_populates="wod", cascade="all, delete")


    def __repr__(self):
        return f"<Wod(id={self.id}, user_email='{self.user_email}', exercise_id={self.exercise_id})>"
    def serialize(self): # to convert to dict
        return {
            "id": self.id,
            "user_email": self.user_email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
class WodExerciseModel(Base):
    __tablename__ = "wod_exercises"
    
    id = Column(Integer, primary_key=True)
    wod_id = Column(Integer, ForeignKey("wods.id", ondelete="CASCADE"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    
    wod = relationship("WodModel", back_populates="exercises")
    exercise = relationship("ExerciseModel")
    
    def serialize(self):
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.name if self.exercise else None
        }
```
Each WOD is linked to a set of exercises via the WodExerciseModel:


### 3. Simulated Failures in WOD Generation

To simulate real-world unpredictability (e.g., external service failures, timeouts), we added a 30% random failure rate to the WOD generation logic using:

```python
if random.random() < 0.3:
    raise Exception("Random failure for testing retries")
```

### 4. Cron Job Script
We created a cron job script that calls the WOD API when triggered. The script contains two functions: one retrieves the access token, and the other makes the API call.

## How can I strengthen the system
1. Extract user microservice to handle user management as well as queue system inside.
2. Add load balancing and support scaling the Coach service with multiple consumer instances.
3. Add advance metrics, alert systems to monitor failures, queue size, and service health.


