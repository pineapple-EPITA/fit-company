# Fitness Database Documentation

This document provides information about the fitness database structure and API endpoints for working with muscle groups and exercises.

## Database Schema

### Muscle Groups Table

The `muscle_groups` table stores information about different muscle groups in the human body.

| Column      | Type         | Description                           |
| ----------- | ------------ | ------------------------------------- |
| id          | SERIAL       | Primary key                           |
| name        | VARCHAR(100) | Name of the muscle group (unique)     |
| body_part   | VARCHAR(50)  | Body part where the muscle is located |
| description | TEXT         | Description of the muscle group       |

### Exercises Table

The `exercises` table stores information about various fitness exercises.

| Column       | Type         | Description                                |
| ------------ | ------------ | ------------------------------------------ |
| id           | SERIAL       | Primary key                                |
| name         | VARCHAR(100) | Name of the exercise (unique)              |
| description  | TEXT         | Description of the exercise                |
| difficulty   | INTEGER      | Difficulty level (1-5)                     |
| equipment    | VARCHAR(100) | Equipment needed for the exercise          |
| instructions | TEXT         | Step-by-step instructions for the exercise |

### Exercise-Muscle Groups Junction Table

The `exercise_muscle_groups` table maps the many-to-many relationship between exercises and muscle groups.

| Column          | Type    | Description                                               |
| --------------- | ------- | --------------------------------------------------------- |
| exercise_id     | INTEGER | Foreign key to exercises table                            |
| muscle_group_id | INTEGER | Foreign key to muscle groups table                        |
| is_primary      | BOOLEAN | Indicates if the muscle group is primary for the exercise |

## API Endpoints

### Muscle Groups

#### Get All Muscle Groups

```
GET /fitness/muscle-groups
```

Returns a list of all muscle groups.

#### Get Specific Muscle Group

```
GET /fitness/muscle-groups/{muscle_group_id}
```

Returns details for a specific muscle group.

### Exercises

#### Get All Exercises

```
GET /fitness/exercises
```

Returns a list of all exercises with their associated muscle groups.

#### Get Exercises by Muscle Group

```
GET /fitness/exercises?muscle_group_id={muscle_group_id}
```

Returns exercises that target a specific muscle group.

#### Get Specific Exercise

```
GET /fitness/exercises/{exercise_id}
```

Returns details for a specific exercise.

## Database Initialization

The fitness database is automatically initialized with muscle groups and exercises when the application starts. This is done through the `init_fitness_data()` function that executes the SQL script at `src/fit/db_init_scripts/init_muscle_groups_exercises.sql`.

The initialization includes:

1. Creation of tables if they don't exist
2. Population of the tables with common muscle groups
3. Population of exercises with descriptions, difficulty levels, and instructions
4. Mapping of exercises to their primary and secondary muscle groups

## Using the Database in Python

You can use the database in your Python code by importing the service functions:

```python
from src.fit.services.fitness_service import (
    get_all_muscle_groups,
    get_muscle_group_by_id,
    get_all_exercises,
    get_exercise_by_id,
    get_exercises_by_muscle_group
)
```

These functions return Pydantic models that can be easily converted to JSON for API responses.
