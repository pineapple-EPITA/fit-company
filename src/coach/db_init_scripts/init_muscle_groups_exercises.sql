-- Initialization script for muscle groups and exercises tables

DROP TABLE muscle_groups CASCADE;
DROP TABLE exercises CASCADE;
DROP TABLE exercise_muscle_groups CASCADE;
-- DROP TABLE user_exercise_history CASCADE;

-- Create muscle groups table
CREATE TABLE IF NOT EXISTS muscle_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    body_part VARCHAR(50) NOT NULL,
    description TEXT
);

-- Create exercises table
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    equipment VARCHAR(100),
    instructions TEXT
);

-- Create junction table for many-to-many relationship between exercises and muscle groups
CREATE TABLE IF NOT EXISTS exercise_muscle_groups (
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE CASCADE,
    muscle_group_id INTEGER REFERENCES muscle_groups(id) ON DELETE CASCADE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (exercise_id, muscle_group_id)
);

-- Populate muscle groups
INSERT INTO muscle_groups (name, body_part, description) VALUES
-- Upper Body
('Pectoralis Major', 'Chest', 'The main chest muscle responsible for pushing movements'),
('Pectoralis Minor', 'Chest', 'A thin, triangular muscle located underneath the pectoralis major'),
('Deltoids', 'Shoulders', 'The rounded muscle group that forms the contour of the shoulder'),
('Trapezius', 'Back', 'A large triangular muscle extending over the back of neck and shoulders'),
('Latissimus Dorsi', 'Back', 'The broadest muscle of the back, involved in pulling movements'),
('Rhomboids', 'Back', 'Muscles that connect the shoulder blades to the spine'),
('Triceps Brachii', 'Arms', 'The large muscle on the back of the upper arm responsible for extending the elbow'),
('Biceps Brachii', 'Arms', 'The muscle on the front of the upper arm that flexes the elbow'),
('Forearms', 'Arms', 'Group of muscles in the lower arm responsible for wrist and finger movements'),

-- Core
('Rectus Abdominis', 'Core', 'The "six-pack" muscle running vertically along the front of the abdomen'),
('Obliques', 'Core', 'The muscles on the sides of the abdomen that rotate and side-bend the torso'),
('Transverse Abdominis', 'Core', 'The deepest abdominal muscle that wraps around the torso'),
('Lower Back', 'Core', 'Group of muscles supporting the lower spine including the erector spinae'),

-- Lower Body
('Quadriceps', 'Legs', 'The large muscle group at the front of the thigh that extends the knee'),
('Hamstrings', 'Legs', 'The group of muscles at the back of the thigh that flex the knee'),
('Gluteus Maximus', 'Glutes', 'The largest and outermost of the three gluteal muscles'),
('Gluteus Medius', 'Glutes', 'The muscle on the outer surface of the pelvis'),
('Calves', 'Legs', 'The muscle group at the back of the lower leg including gastrocnemius and soleus'),
('Hip Flexors', 'Hips', 'The group of muscles that allow you to lift your knee toward your body'),
('Adductors', 'Legs', 'The muscles of the inner thigh that pull the legs together');

-- Populate exercises
INSERT INTO exercises (name, description, difficulty, equipment, instructions) VALUES
-- Chest exercises
('Bench Press', 'A compound exercise that targets the chest, shoulders, and triceps', 3, 'Barbell, Bench', 'Lie on a bench, lower the barbell to your chest, and push it back up'),
('Push-ups', 'A bodyweight exercise targeting the chest, shoulders, and triceps', 2, 'None', 'Start in a plank position with hands under shoulders, lower body until chest nearly touches the floor, then push back up'),
('Dumbbell Flyes', 'An isolation exercise for the chest', 2, 'Dumbbells, Bench', 'Lie on a bench holding dumbbells above your chest, lower them out to the sides in an arc motion, then bring them back up'),

-- Back exercises
('Pull-ups', 'A compound bodyweight exercise for the back and biceps', 4, 'Pull-up bar', 'Hang from a bar with palms facing away, pull yourself up until chin clears the bar'),
('Barbell Rows', 'A compound exercise for the back, biceps, and shoulders', 3, 'Barbell', 'Bend at the hips holding a barbell, pull it to your lower chest while keeping your back straight'),
('Lat Pulldowns', 'A machine exercise targeting the latissimus dorsi', 2, 'Cable machine', 'Sit at a lat pulldown machine, grab the bar wide, and pull it down to your upper chest'),

-- Shoulder exercises
('Overhead Press', 'A compound exercise for the shoulders and triceps', 3, 'Barbell or Dumbbells', 'Stand holding weights at shoulder level, press them overhead until arms are extended'),
('Lateral Raises', 'An isolation exercise for the lateral deltoids', 2, 'Dumbbells', 'Stand holding dumbbells at your sides, raise them out to the sides until parallel with the floor'),
('Face Pulls', 'An exercise for the rear deltoids and upper back', 2, 'Cable machine, Rope attachment', 'Pull a rope attachment towards your face with elbows high'),

-- Arm exercises
('Bicep Curls', 'An isolation exercise for the biceps', 1, 'Dumbbells or Barbell', 'Hold weights with arms extended, curl them up towards your shoulders'),
('Tricep Pushdowns', 'An isolation exercise for the triceps', 1, 'Cable machine', 'Push a cable attachment down from chest level until arms are extended'),
('Hammer Curls', 'A bicep curl variation that also targets the forearms', 1, 'Dumbbells', 'Perform bicep curls with palms facing each other'),

-- Core exercises
('Crunches', 'An isolation exercise for the rectus abdominis', 1, 'None', 'Lie on your back with knees bent, curl your upper body towards your knees'),
('Plank', 'A static exercise for the entire core', 2, 'None', 'Hold a push-up position but with weight on forearms, keeping body straight'),
('Russian Twists', 'A rotational exercise for the obliques', 2, 'Weight (optional)', 'Sit with knees bent and lean back slightly, twist torso side to side'),

-- Leg exercises
('Squats', 'A compound exercise primarily for the quadriceps and glutes', 3, 'Barbell (optional)', 'Stand with feet shoulder-width apart, bend knees to lower body, then stand back up'),
('Deadlifts', 'A compound exercise for the entire posterior chain', 4, 'Barbell', 'Bend at hips and knees to grab a barbell, stand up straight while keeping back flat'),
('Lunges', 'A unilateral exercise for legs and glutes', 2, 'Dumbbells (optional)', 'Step forward with one leg and lower your body until both knees are bent at 90 degrees'),
('Leg Press', 'A machine-based compound leg exercise', 2, 'Leg press machine', 'Push weight away by extending legs from a seated position'),
('Calf Raises', 'An isolation exercise for the calves', 1, 'Step or calf raise machine', 'Raise heels off the ground by extending ankles, then lower back down');

-- Link exercises to muscle groups (primary and secondary)
-- Bench Press
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Bench Press'), (SELECT id FROM muscle_groups WHERE name = 'Pectoralis Major'), TRUE),
((SELECT id FROM exercises WHERE name = 'Bench Press'), (SELECT id FROM muscle_groups WHERE name = 'Deltoids'), FALSE),
((SELECT id FROM exercises WHERE name = 'Bench Press'), (SELECT id FROM muscle_groups WHERE name = 'Triceps Brachii'), FALSE);

-- Push-ups
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Push-ups'), (SELECT id FROM muscle_groups WHERE name = 'Pectoralis Major'), TRUE),
((SELECT id FROM exercises WHERE name = 'Push-ups'), (SELECT id FROM muscle_groups WHERE name = 'Deltoids'), FALSE),
((SELECT id FROM exercises WHERE name = 'Push-ups'), (SELECT id FROM muscle_groups WHERE name = 'Triceps Brachii'), FALSE),
((SELECT id FROM exercises WHERE name = 'Push-ups'), (SELECT id FROM muscle_groups WHERE name = 'Rectus Abdominis'), FALSE);

-- Dumbbell Flyes
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Dumbbell Flyes'), (SELECT id FROM muscle_groups WHERE name = 'Pectoralis Major'), TRUE),
((SELECT id FROM exercises WHERE name = 'Dumbbell Flyes'), (SELECT id FROM muscle_groups WHERE name = 'Pectoralis Minor'), FALSE);

-- Pull-ups
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Pull-ups'), (SELECT id FROM muscle_groups WHERE name = 'Latissimus Dorsi'), TRUE),
((SELECT id FROM exercises WHERE name = 'Pull-ups'), (SELECT id FROM muscle_groups WHERE name = 'Biceps Brachii'), FALSE),
((SELECT id FROM exercises WHERE name = 'Pull-ups'), (SELECT id FROM muscle_groups WHERE name = 'Forearms'), FALSE);

-- Barbell Rows
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Barbell Rows'), (SELECT id FROM muscle_groups WHERE name = 'Latissimus Dorsi'), TRUE),
((SELECT id FROM exercises WHERE name = 'Barbell Rows'), (SELECT id FROM muscle_groups WHERE name = 'Rhomboids'), FALSE),
((SELECT id FROM exercises WHERE name = 'Barbell Rows'), (SELECT id FROM muscle_groups WHERE name = 'Biceps Brachii'), FALSE);

-- Lat Pulldowns
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Lat Pulldowns'), (SELECT id FROM muscle_groups WHERE name = 'Latissimus Dorsi'), TRUE),
((SELECT id FROM exercises WHERE name = 'Lat Pulldowns'), (SELECT id FROM muscle_groups WHERE name = 'Biceps Brachii'), FALSE);

-- Overhead Press
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Overhead Press'), (SELECT id FROM muscle_groups WHERE name = 'Deltoids'), TRUE),
((SELECT id FROM exercises WHERE name = 'Overhead Press'), (SELECT id FROM muscle_groups WHERE name = 'Triceps Brachii'), FALSE);

-- Lateral Raises
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Lateral Raises'), (SELECT id FROM muscle_groups WHERE name = 'Deltoids'), TRUE);

-- Face Pulls
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Face Pulls'), (SELECT id FROM muscle_groups WHERE name = 'Deltoids'), TRUE),
((SELECT id FROM exercises WHERE name = 'Face Pulls'), (SELECT id FROM muscle_groups WHERE name = 'Trapezius'), FALSE),
((SELECT id FROM exercises WHERE name = 'Face Pulls'), (SELECT id FROM muscle_groups WHERE name = 'Rhomboids'), FALSE);

-- Bicep Curls
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Bicep Curls'), (SELECT id FROM muscle_groups WHERE name = 'Biceps Brachii'), TRUE),
((SELECT id FROM exercises WHERE name = 'Bicep Curls'), (SELECT id FROM muscle_groups WHERE name = 'Forearms'), FALSE);

-- Tricep Pushdowns
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Tricep Pushdowns'), (SELECT id FROM muscle_groups WHERE name = 'Triceps Brachii'), TRUE);

-- Hammer Curls
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Hammer Curls'), (SELECT id FROM muscle_groups WHERE name = 'Biceps Brachii'), TRUE),
((SELECT id FROM exercises WHERE name = 'Hammer Curls'), (SELECT id FROM muscle_groups WHERE name = 'Forearms'), TRUE);

-- Crunches
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Crunches'), (SELECT id FROM muscle_groups WHERE name = 'Rectus Abdominis'), TRUE);

-- Plank
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Plank'), (SELECT id FROM muscle_groups WHERE name = 'Rectus Abdominis'), TRUE),
((SELECT id FROM exercises WHERE name = 'Plank'), (SELECT id FROM muscle_groups WHERE name = 'Transverse Abdominis'), TRUE),
((SELECT id FROM exercises WHERE name = 'Plank'), (SELECT id FROM muscle_groups WHERE name = 'Deltoids'), FALSE),
((SELECT id FROM exercises WHERE name = 'Plank'), (SELECT id FROM muscle_groups WHERE name = 'Lower Back'), FALSE);

-- Russian Twists
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Russian Twists'), (SELECT id FROM muscle_groups WHERE name = 'Obliques'), TRUE),
((SELECT id FROM exercises WHERE name = 'Russian Twists'), (SELECT id FROM muscle_groups WHERE name = 'Rectus Abdominis'), FALSE);

-- Squats
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Squats'), (SELECT id FROM muscle_groups WHERE name = 'Quadriceps'), TRUE),
((SELECT id FROM exercises WHERE name = 'Squats'), (SELECT id FROM muscle_groups WHERE name = 'Gluteus Maximus'), TRUE),
((SELECT id FROM exercises WHERE name = 'Squats'), (SELECT id FROM muscle_groups WHERE name = 'Hamstrings'), FALSE),
((SELECT id FROM exercises WHERE name = 'Squats'), (SELECT id FROM muscle_groups WHERE name = 'Lower Back'), FALSE);

-- Deadlifts
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Deadlifts'), (SELECT id FROM muscle_groups WHERE name = 'Lower Back'), TRUE),
((SELECT id FROM exercises WHERE name = 'Deadlifts'), (SELECT id FROM muscle_groups WHERE name = 'Gluteus Maximus'), TRUE),
((SELECT id FROM exercises WHERE name = 'Deadlifts'), (SELECT id FROM muscle_groups WHERE name = 'Hamstrings'), TRUE),
((SELECT id FROM exercises WHERE name = 'Deadlifts'), (SELECT id FROM muscle_groups WHERE name = 'Quadriceps'), FALSE),
((SELECT id FROM exercises WHERE name = 'Deadlifts'), (SELECT id FROM muscle_groups WHERE name = 'Trapezius'), FALSE),
((SELECT id FROM exercises WHERE name = 'Deadlifts'), (SELECT id FROM muscle_groups WHERE name = 'Forearms'), FALSE);

-- Lunges
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Lunges'), (SELECT id FROM muscle_groups WHERE name = 'Quadriceps'), TRUE),
((SELECT id FROM exercises WHERE name = 'Lunges'), (SELECT id FROM muscle_groups WHERE name = 'Gluteus Maximus'), TRUE),
((SELECT id FROM exercises WHERE name = 'Lunges'), (SELECT id FROM muscle_groups WHERE name = 'Hamstrings'), FALSE);

-- Leg Press
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Leg Press'), (SELECT id FROM muscle_groups WHERE name = 'Quadriceps'), TRUE),
((SELECT id FROM exercises WHERE name = 'Leg Press'), (SELECT id FROM muscle_groups WHERE name = 'Gluteus Maximus'), FALSE),
((SELECT id FROM exercises WHERE name = 'Leg Press'), (SELECT id FROM muscle_groups WHERE name = 'Hamstrings'), FALSE);

-- Calf Raises
INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary) VALUES
((SELECT id FROM exercises WHERE name = 'Calf Raises'), (SELECT id FROM muscle_groups WHERE name = 'Calves'), TRUE); 