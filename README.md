# Tasks - FastAPI CRUD API with Pluggable Storage (SQLite / PostgreSQL)

A simple task management API built with FastAPI demonstrating full CRUD operations with **pluggable persistence** — swap between SQLite (dev) and PostgreSQL (prod/Docker) without changing routes or services.

## Features

- **GET /** - API metadata and available endpoints
- **GET /health** - Health check endpoint
- **GET /tasks** - List all tasks (supports `?search=`, `?done=`, `?sort=`)
- **GET /tasks/{id}** - Get a single task by ID (404 if not found)
- **POST /tasks** - Create a new task (validates title, returns 201)
- **PUT /tasks/{id}** - Update task title and/or done status (404 if not found)
- **DELETE /tasks/{id}** - Delete a task (204 No Content, 404 if not found)
- **GET /stats** - Get task statistics (total, completed, pending)

Data persists across restarts using either **SQLite** (default) or **PostgreSQL** (via Docker).

## Quick Start (SQLite - Default)

```bash
# Clone and enter directory
git clone https://github.com/ZakZap16/CRUD-API
cd Assignment1

# Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run the server
python main.py
```

Server starts at **http://localhost:8000**  
Swagger UI at **http://localhost:8000/docs**

On first run, the database is auto-created with 3 seed tasks.

## Quick Start (PostgreSQL via Docker)

```bash
# Start PostgreSQL + API together
docker compose up -d --build

# API at http://localhost:8000 (connected to Postgres)
# Postgres at localhost:5432 (user: postgres, pass: postgres, db: tasks)

# Stop stack (to keep data in Docker volume)
docker compose down

# Stop and remove everything including the data
docker compose down -v
```

**Configuration**: Copy `.env.example` to `.env` and set `DATABASE_URL=postgresql://postgres:postgres@db:5432/tasks`

## Architecture: Repository Pattern

The app uses a **repository interface** (`TaskRepository` in `repository.py`) so storage can be swapped without touching routes or services.

```
Routes → TaskRepository (interface) → DI provides implementation
                                        ├── SQLiteTaskRepository  (DATABASE_URL=sqlite://...)
                                        └── PostgresTaskRepository (DATABASE_URL=postgresql://...)
```

**Changing storage = one line in `dependencies.py`**. Routes and services import only the abstract interface.

## Persistence Verification

### SQLite (Local)

```bash
# 1. Start server
python -m app.main

# 2. Create a task
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Test persistence"}'

# 3. Restart server (Ctrl+C, then python main.py)

# 4. Verify task exists
curl http://localhost:8000/tasks
# → Task persists in tasks.db
```

### PostgreSQL (Docker)

```bash
# 1. Start stack
docker compose up -d --build

# 2. Create a task
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Docker persistence test"}'

# 3. Restart containers
docker compose restart

# 4. Verify task still exists
curl http://localhost:8000/tasks
# → Task persists in Docker volume (postgres_data)
```

**Tested**: Data survives both app restart and full container restart.

## Endpoints

| Method | Endpoint      | Description            | Status Codes  |
| ------ | ------------- | ---------------------- | ------------- |
| GET    | `/`           | API info               | 200           |
| GET    | `/health`     | Health check           | 200           |
| GET    | `/tasks`      | List all tasks         | 200           |
| GET    | `/tasks`      | Search: `?search=term` | 200           |
| GET    | `/tasks`      | Filter: `?done=true`   | 200           |
| GET    | `/tasks`      | Sort: `?sort=title`    | 200           |
| GET    | `/tasks/{id}` | Get task by ID         | 200, 404      |
| POST   | `/tasks`      | Create task            | 201, 422      |
| PUT    | `/tasks/{id}` | Update task            | 200, 404, 422 |
| DELETE | `/tasks/{id}` | Delete task            | 204, 404      |
| GET    | `/stats`      | Get statistics         | 200           |

### Query Parameters for GET /tasks

| Parameter | Values             | Description                               |
| --------- | ------------------ | ----------------------------------------- |
| `search`  | string             | Partial match on title (case-insensitive) |
| `done`    | `true` / `false`   | Filter by completion status               |
| `sort`    | `title` / `-title` | Sort alphabetically (asc/desc)            |

## Example Usage

### Create a task

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

### List all tasks

```bash
curl -i http://localhost:8000/tasks
```

### Get a single task

```bash
curl -i http://localhost:8000/tasks/1
```

### Update a task

```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'
```

### Delete a task

```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```

### Get statistics

```bash
curl -i http://localhost:8000/stats
```

### Validation error (empty title)

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":""}'
```

Returns **422** with validation details.

### Not found error

```bash
curl -i http://localhost:8000/tasks/999
```

Returns **404** with `{"error": "Task not found"}`.

## Swagger UI

Interactive API documentation at **http://localhost:8000/docs**

![Swagger UI](SwaggerUI.png)

## Database

### SQLite (Default - Development)

- **File**: `./tasks.db`
- **Zero config**, single file, cross-platform
- Auto-created on first run with 3 seed tasks

### PostgreSQL (Production / Docker)

- **Connection**: `postgresql://postgres:postgres@db:5432/tasks` (inside Docker)
- **Volume**: `postgres_data` persists data across container restarts
- **Init script**: `init.sql` creates table + seeds 3 tasks on first container start

### Schema (Both)

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tasks_title ON tasks (title);
```

### Example SQL Queries

Run in DB Browser (SQLite) or pgAdmin/psql (PostgreSQL):

```sql
-- List every task
SELECT * FROM tasks;

-- Show only completed tasks
SELECT * FROM tasks WHERE done = true;

-- Count all tasks
SELECT COUNT(*) FROM tasks;

-- Mark every task as completed
UPDATE tasks SET done = true;

-- Delete all completed tasks
DELETE FROM tasks WHERE done = true;

-- Search tasks by title (like API's ?search=)
SELECT * FROM tasks WHERE title ILIKE '%API%';

-- Get statistics (like API's /stats)
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN done THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN NOT done THEN 1 ELSE 0 END) as pending
FROM tasks;
```

## Project Structure

```
Assignment1/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── sqlite.py
│   │   └── postgres.py
│   └── routes/
│       └── __init__.py
├── docker/
│   ├── Dockerfile
│   └── init.sql
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── README.md
├── tasks.db
├── SwaggerUI.png
└── database-viewer.png
```

## Requirements

- Python 3.10+
- Docker & Docker Compose (for PostgreSQL mode)

Install Python deps:

```bash
pip install -r requirements.txt
```

## Observation

- **Data persists across restarts** — both SQLite file (local) and container restarts (Docker/Postgres)
- **Repository pattern** — storage backend swapped via `DATABASE_URL` without touching routes/services
- **Assignment 2**: SQLite implementation with all optional extras (search, filter, sort, stats, timestamps)
- **Assignment 3**: Docker + PostgreSQL, proven persistence, repo pattern documented
