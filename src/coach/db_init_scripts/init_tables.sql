CREATE TABLE IF NOT EXISTS users (
    email VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    weight FLOAT,
    height FLOAT,
    fitness_goal VARCHAR,
    onboarded VARCHAR DEFAULT 'false' NOT NULL
);

CREATE TABLE IF NOT EXISTS wods (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR NOT NULL REFERENCES users(email),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    exercises JSONB NOT NULL,
    generated_at VARCHAR NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_wods_user_date 
ON wods(user_email, date); 