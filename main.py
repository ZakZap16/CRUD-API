from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(
    title="Task API",
    version="1.0.0",
    description="A simple task management API with CRUD operations",
    docs_url="/docs",
    redoc_url="/redoc"
)

tasks: List[Dict] = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a REST API", "done": False},
    {"id": 3, "title": "Deploy to production", "done": True},
]
next_id = 4


class Task(BaseModel):
    id: int
    title: str
    done: bool


@app.get(
    "/",
    summary="Root endpoint",
    description="Returns API metadata and available endpoints"
)
async def root():
    return {
        "name": "Task API",
        "version": "1.0.0",
        "endpoints": ["/tasks"]
    }


@app.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the API"
)
async def health():
    return {"status": "ok"}


@app.get(
    "/tasks",
    response_model=List[Task],
    summary="List all tasks",
    description="Returns a list of all tasks"
)
async def list_tasks():
    return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Get a single task",
    description="Returns a task by its ID"
)
async def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)