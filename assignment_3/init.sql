CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, done)
SELECT 'Complete Assignment', TRUE
WHERE NOT EXISTS (SELECT 1 FROM tasks);

INSERT INTO tasks (title, done)
SELECT 'Go to the gym', TRUE
WHERE NOT EXISTS (SELECT 1 FROM tasks WHERE title = 'Go to the gym');

INSERT INTO tasks (title, done)
SELECT 'Write about today in journal', FALSE
WHERE NOT EXISTS (SELECT 1 FROM tasks WHERE title = 'Write about today in journal');
