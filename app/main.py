import uvicorn
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlmodel import Session

from app.database import create_db_and_tables, get_session
from app.dependencies import get_task_repository
from app.repositories.base import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, StatsResponse
from app.routes import auth, public

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # Seed database on startup
    with next(get_session()) as session:
        repo = get_task_repository(session)
        repo.seed_if_empty(session)
    yield


app = FastAPI(
    title="Task API",
    version="3.0.0",
    description="Task management API with pluggable storage (SQLite/PostgreSQL)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(auth.router)
app.include_router(public.router)


@app.get(
    "/",
    summary="Root endpoint",
    description="Returns API metadata and available endpoints"
)
async def root():
    return {
        "name": "Task API",
        "version": "3.0.0",
        "endpoints": [
            "/tasks", "/tasks/{task_id}", "/stats",
            "/auth/signup", "/auth/login",
            "/public/info", "/protected/profile"
        ]
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
    response_model=List[TaskRead],
    summary="List all tasks",
    description="Returns a list of all tasks with optional filtering and sorting"
)
async def list_tasks(
    search: Optional[str] = Query(None, description="Search tasks by title (partial match)"),
    done: Optional[bool] = Query(None, description="Filter by completion status"),
    sort: Optional[str] = Query(None, description="Sort by title: 'title' or '-title'"),
    repo: TaskRepository = Depends(get_task_repository),
    db: Session = Depends(get_session),
):
    tasks = repo.get_all(db, search=search, done=done, sort=sort)
    return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=TaskRead,
    summary="Get a single task",
    description="Returns a task by its ID"
)
async def get_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository),
    db: Session = Depends(get_session),
):
    task = repo.get_by_id(db, task_id)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return task


@app.post(
    "/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task with the given title"
)
async def create_task(
    task_data: TaskCreate,
    repo: TaskRepository = Depends(get_task_repository),
    db: Session = Depends(get_session),
):
    task = repo.create(db, task_data)
    return task


@app.put(
    "/tasks/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Updates a task by ID. Can update title and/or done status."
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    repo: TaskRepository = Depends(get_task_repository),
    db: Session = Depends(get_session),
):
    task = repo.update(db, task_id, task_data)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Deletes a task by ID"
)
async def delete_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository),
    db: Session = Depends(get_session),
):
    deleted = repo.delete(db, task_id)
    if not deleted:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return None


@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get task statistics",
    description="Returns counts of total, completed, and pending tasks"
)
async def get_stats(
    repo: TaskRepository = Depends(get_task_repository),
    db: Session = Depends(get_session),
):
    stats = repo.get_stats(db)
    return stats


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)