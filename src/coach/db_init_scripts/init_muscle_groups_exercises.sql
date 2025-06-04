-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    weight INTEGER,
    height INTEGER,
    fitness_goal VARCHAR,
    onboarded VARCHAR NOT NULL DEFAULT 'false'
);

-- Create muscle groups table if it doesn't exist
CREATE TABLE IF NOT EXISTS muscle_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    body_part VARCHAR(50) NOT NULL,
    description TEXT
);

-- Create exercises table if it doesn't exist
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    equipment VARCHAR(100),
    instructions TEXT
);

-- Create junction table for many-to-many relationship between exercises and muscle groups if it doesn't exist
CREATE TABLE IF NOT EXISTS exercise_muscle_groups (
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE CASCADE,
    muscle_group_id INTEGER REFERENCES muscle_groups(id) ON DELETE CASCADE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (exercise_id, muscle_group_id)
);

-- Create wods table if it doesn't exist
CREATE TABLE IF NOT EXISTS wods (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR NOT NULL REFERENCES users(email),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    exercises JSONB NOT NULL,
    generated_at VARCHAR NOT NULL
);

INSERT INTO muscle_groups (name, body_part, description)
SELECT name, body_part, description
FROM (VALUES
    ('Pectoralis Major', 'Chest', 'The main chest muscle responsible for pushing movements'),
    ('Pectoralis Minor', 'Chest', 'A thin, triangular muscle located underneath the pectoralis major'),
    ('Deltoids', 'Shoulders', 'The rounded muscle group that forms the contour of the shoulder'),
    ('Trapezius', 'Back', 'A large triangular muscle extending over the back of neck and shoulders'),
    ('Latissimus Dorsi', 'Back', 'The broadest muscle of the back, involved in pulling movements'),
    ('Rhomboids', 'Back', 'Muscles that connect the shoulder blades to the spine'),
    ('Triceps Brachii', 'Arms', 'The large muscle on the back of the upper arm responsible for extending the elbow'),
    ('Biceps Brachii', 'Arms', 'The muscle on the front of the upper arm that flexes the elbow'),
    ('Forearms', 'Arms', 'Group of muscles in the lower arm responsible for wrist and finger movements'),
    ('Rectus Abdominis', 'Core', 'The "six-pack" muscle running vertically along the front of the abdomen'),
    ('Obliques', 'Core', 'The muscles on the sides of the abdomen that rotate and side-bend the torso'),
    ('Transverse Abdominis', 'Core', 'The deepest abdominal muscle that wraps around the torso'),
    ('Lower Back', 'Core', 'Group of muscles supporting the lower spine including the erector spinae'),
    ('Quadriceps', 'Legs', 'The large muscle group at the front of the thigh that extends the knee'),
    ('Hamstrings', 'Legs', 'The group of muscles at the back of the thigh that flex the knee'),
    ('Gluteus Maximus', 'Glutes', 'The largest and outermost of the three gluteal muscles'),
    ('Gluteus Medius', 'Glutes', 'The muscle on the outer surface of the pelvis'),
    ('Calves', 'Legs', 'The muscle group at the back of the lower leg including gastrocnemius and soleus'),
    ('Hip Flexors', 'Hips', 'The group of muscles that allow you to lift your knee toward your body'),
    ('Adductors', 'Legs', 'The muscles of the inner thigh that pull the legs together')
) AS new_muscle_groups(name, body_part, description)
WHERE NOT EXISTS (SELECT 1 FROM muscle_groups WHERE muscle_groups.name = new_muscle_groups.name);

INSERT INTO exercises (name, description, difficulty, equipment, instructions)
SELECT name, description, difficulty, equipment, instructions
FROM (VALUES
    ('Bench Press', 'A compound exercise that targets the chest, shoulders, and triceps', 3, 'Barbell, Bench', 'Lie on a bench, lower the barbell to your chest, and push it back up'),
    ('Push-ups', 'A bodyweight exercise targeting the chest, shoulders, and triceps', 2, 'None', 'Start in a plank position with hands under shoulders, lower body until chest nearly touches the floor, then push back up'),
    ('Dumbbell Flyes', 'An isolation exercise for the chest', 2, 'Dumbbells, Bench', 'Lie on a bench holding dumbbells above your chest, lower them out to the sides in an arc motion, then bring them back up'),
    ('Pull-ups', 'A compound bodyweight exercise for the back and biceps', 4, 'Pull-up bar', 'Hang from a bar with palms facing away, pull yourself up until chin clears the bar'),
    ('Barbell Rows', 'A compound exercise for the back, biceps, and shoulders', 3, 'Barbell', 'Bend at the hips holding a barbell, pull it to your lower chest while keeping your back straight'),
    ('Lat Pulldowns', 'A machine exercise targeting the latissimus dorsi', 2, 'Cable machine', 'Sit at a lat pulldown machine, grab the bar wide, and pull it down to your upper chest'),
    ('Overhead Press', 'A compound exercise for the shoulders and triceps', 3, 'Barbell or Dumbbells', 'Stand holding weights at shoulder level, press them overhead until arms are extended'),
    ('Lateral Raises', 'An isolation exercise for the lateral deltoids', 2, 'Dumbbells', 'Stand holding dumbbells at your sides, raise them out to the sides until parallel with the floor'),
    ('Face Pulls', 'An exercise for the rear deltoids and upper back', 2, 'Cable machine, Rope attachment', 'Pull a rope attachment towards your face with elbows high'),
    ('Bicep Curls', 'An isolation exercise for the biceps', 1, 'Dumbbells or Barbell', 'Hold weights with arms extended, curl them up towards your shoulders'),
    ('Tricep Pushdowns', 'An isolation exercise for the triceps', 1, 'Cable machine', 'Push a cable attachment down from chest level until arms are extended'),
    ('Hammer Curls', 'A bicep curl variation that also targets the forearms', 1, 'Dumbbells', 'Perform bicep curls with palms facing each other'),
    ('Crunches', 'An isolation exercise for the rectus abdominis', 1, 'None', 'Lie on your back with knees bent, curl your upper body towards your knees'),
    ('Plank', 'A static exercise for the entire core', 2, 'None', 'Hold a push-up position but with weight on forearms, keeping body straight'),
    ('Russian Twists', 'A rotational exercise for the obliques', 2, 'Weight (optional)', 'Sit with knees bent and lean back slightly, twist torso side to side'),
    ('Squats', 'A compound exercise primarily for the quadriceps and glutes', 3, 'Barbell (optional)', 'Stand with feet shoulder-width apart, bend knees to lower body, then stand back up'),
    ('Deadlifts', 'A compound exercise for the entire posterior chain', 4, 'Barbell', 'Bend at hips and knees to grab a barbell, stand up straight while keeping back flat'),
    ('Lunges', 'A unilateral exercise for legs and glutes', 2, 'Dumbbells (optional)', 'Step forward with one leg and lower your body until both knees are bent at 90 degrees'),
    ('Leg Press', 'A machine-based compound leg exercise', 2, 'Leg press machine', 'Push weight away by extending legs from a seated position'),
    ('Calf Raises', 'An isolation exercise for the calves', 1, 'Step or calf raise machine', 'Raise heels off the ground by extending ankles, then lower back down')
) AS new_exercises(name, description, difficulty, equipment, instructions)
WHERE NOT EXISTS (SELECT 1 FROM exercises WHERE exercises.name = new_exercises.name);

INSERT INTO exercise_muscle_groups (exercise_id, muscle_group_id, is_primary)
SELECT e.id, m.id, is_primary
FROM (VALUES
    ('Bench Press', 'Pectoralis Major', TRUE),
    ('Bench Press', 'Deltoids', FALSE),
    ('Bench Press', 'Triceps Brachii', FALSE),
    ('Push-ups', 'Pectoralis Major', TRUE),
    ('Push-ups', 'Deltoids', FALSE),
    ('Push-ups', 'Triceps Brachii', FALSE),
    ('Push-ups', 'Rectus Abdominis', FALSE),
    ('Dumbbell Flyes', 'Pectoralis Major', TRUE),
    ('Dumbbell Flyes', 'Pectoralis Minor', FALSE),
    ('Pull-ups', 'Latissimus Dorsi', TRUE),
    ('Pull-ups', 'Biceps Brachii', FALSE),
    ('Pull-ups', 'Forearms', FALSE),
    ('Barbell Rows', 'Latissimus Dorsi', TRUE),
    ('Barbell Rows', 'Rhomboids', FALSE),
    ('Barbell Rows', 'Biceps Brachii', FALSE),
    ('Lat Pulldowns', 'Latissimus Dorsi', TRUE),
    ('Lat Pulldowns', 'Biceps Brachii', FALSE),
    ('Overhead Press', 'Deltoids', TRUE),
    ('Overhead Press', 'Triceps Brachii', FALSE),
    ('Lateral Raises', 'Deltoids', TRUE),
    ('Face Pulls', 'Deltoids', TRUE),
    ('Face Pulls', 'Trapezius', FALSE),
    ('Face Pulls', 'Rhomboids', FALSE),
    ('Bicep Curls', 'Biceps Brachii', TRUE),
    ('Bicep Curls', 'Forearms', FALSE),
    ('Tricep Pushdowns', 'Triceps Brachii', TRUE),
    ('Hammer Curls', 'Biceps Brachii', TRUE),
    ('Hammer Curls', 'Forearms', TRUE),
    ('Crunches', 'Rectus Abdominis', TRUE),
    ('Plank', 'Rectus Abdominis', TRUE),
    ('Plank', 'Transverse Abdominis', TRUE),
    ('Plank', 'Deltoids', FALSE),
    ('Plank', 'Lower Back', FALSE),
    ('Russian Twists', 'Obliques', TRUE),
    ('Russian Twists', 'Rectus Abdominis', FALSE),
    ('Squats', 'Quadriceps', TRUE),
    ('Squats', 'Gluteus Maximus', TRUE),
    ('Squats', 'Hamstrings', FALSE),
    ('Squats', 'Lower Back', FALSE),
    ('Deadlifts', 'Lower Back', TRUE),
    ('Deadlifts', 'Gluteus Maximus', TRUE),
    ('Deadlifts', 'Hamstrings', TRUE),
    ('Deadlifts', 'Quadriceps', FALSE),
    ('Deadlifts', 'Trapezius', FALSE),
    ('Deadlifts', 'Forearms', FALSE),
    ('Lunges', 'Quadriceps', TRUE),
    ('Lunges', 'Gluteus Maximus', TRUE),
    ('Lunges', 'Hamstrings', FALSE),
    ('Leg Press', 'Quadriceps', TRUE),
    ('Leg Press', 'Gluteus Maximus', FALSE),
    ('Leg Press', 'Hamstrings', FALSE),
    ('Calf Raises', 'Calves', TRUE)
) AS new_links(exercise_name, muscle_group_name, is_primary)
JOIN exercises e ON e.name = new_links.exercise_name
JOIN muscle_groups m ON m.name = new_links.muscle_group_name
WHERE NOT EXISTS (
    SELECT 1 FROM exercise_muscle_groups emg 
    WHERE emg.exercise_id = e.id AND emg.muscle_group_id = m.id
); 