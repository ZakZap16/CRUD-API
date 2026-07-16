# Task API - FastAPI CRUD Assignment

A simple task management API built with FastAPI demonstrating full CRUD operations on an in-memory task list. Includes automatic Swagger UI documentation at `/docs`.

## Features

- **GET /** - API metadata and available endpoints
- **GET /health** - Health check endpoint
- **GET /tasks** - List all tasks
- **GET /tasks/{id}** - Get a single task by ID (404 if not found)
- **POST /tasks** - Create a new task (validates title, returns 201)
- **PUT /tasks/{id}** - Update task title and/or done status (404 if not found)
- **DELETE /tasks/{id}** - Delete a task (204 No Content, 404 if not found)

All data stored in memory (resets on server restart).

## Quick Start

```bash
# Clone and enter directory
git clone <your-repo-url>
cd Assignment1

# Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn

# Run the server
python main.py
```

Server starts at **http://localhost:8000**  
Swagger UI available at **http://localhost:8000/docs**

## Endpoints

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| GET | `/` | API info | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List all tasks | 200 |
| GET | `/tasks/{id}` | Get task by ID | 200, 404 |
| POST | `/tasks` | Create task | 201, 422 |
| PUT | `/tasks/{id}` | Update task | 200, 404, 422 |
| DELETE | `/tasks/{id}` | Delete task | 204, 404 |

## Example Usage

### Create a task
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

**Response:**
```
HTTP/1.1 201 Created
content-type: application/json
content-length: 38

{"id":4,"title":"Buy milk","done":false}
```

### List all tasks
```bash
curl -i http://localhost:8000/tasks
```

**Response:**
```
HTTP/1.1 200 OK
content-type: application/json
content-length: 117

[{"id":1,"title":"Learn FastAPI","done":false},{"id":2,"title":"Build a REST API","done":false},{"id":3,"title":"Deploy to production","done":true}]
```

### Get a single task
```bash
curl -i http://localhost:8000/tasks/1
```

**Response:**
```
HTTP/1.1 200 OK
content-type: application/json
content-length: 44

{"id":1,"title":"Learn FastAPI","done":false}
```

### Update a task
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'
```

**Response:**
```
HTTP/1.1 200 OK
content-type: application/json
content-length: 44

{"id":1,"title":"Learn FastAPI","done":true}
```

### Delete a task
```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```

**Response:**
```
HTTP/1.1 204 No Content
```

### Validation error (empty title)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":""}'
```

**Response:**
```
HTTP/1.1 422 Unprocessable Entity
content-type: application/json
content-length: 145

{"detail":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}}]}
```

### Not found error
```bash
curl -i http://localhost:8000/tasks/999
```

**Response:**
```
HTTP/1.1 404 Not Found
content-type: application/json
content-length: 30

{"detail":"Task 999 not found"}
```

## Swagger UI

Interactive API documentation available at **http://localhost:8000/docs**

![Swagger UI](swagger-screenshot.png)

*Replace `swagger-screenshot.png` with your actual screenshot*

## Project Structure

```
Assignment1/
├── main.py          # FastAPI application
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Requirements

- Python 3.10+
- fastapi
- uvicorn
- pydantic

Install with:
```bash
pip install -r requirements.txt
```

## License

MIT