from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

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


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    done: Optional[bool] = None


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


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task with the given title"
)
async def create_task(task_data: TaskCreate):
    global next_id
    new_task = {"id": next_id, "title": task_data.title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Update a task",
    description="Updates a task by ID. Can update title and/or done status."
)
async def update_task(task_id: int, task_data: TaskUpdate):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            if task_data.title is not None:
                tasks[i]["title"] = task_data.title
            if task_data.done is not None:
                tasks[i]["done"] = task_data.done
            return tasks[i]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Deletes a task by ID"
)
async def delete_task(task_id: int):
    global tasks
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)