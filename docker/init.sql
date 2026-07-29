-- PostgreSQL initialization script
-- Runs automatically on first container startup via docker-entrypoint-initdb.d

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on title for search performance
CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks (title);

-- Seed 3 example tasks only if table is empty
INSERT INTO tasks (title, done, created_at, updated_at)
SELECT * FROM (VALUES
    ('Learn FastAPI', FALSE, NOW(), NOW()),
    ('Build a REST API', FALSE, NOW(), NOW()),
    ('Deploy to production', TRUE, NOW(), NOW())
) AS v(title, done, created_at, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM tasks);