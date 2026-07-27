import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlmodel import Field, Session, SQLModel, create_engine, select


sqlite_file = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file}"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    done: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    done: Optional[bool] = None


class TaskRead(BaseModel):
    id: int
    title: str
    done: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total: int
    completed: int
    pending: int


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        count = session.exec(select(Task)).first()
        if count is None:
            seed_tasks = [
                Task(title="Learn FastAPI", done=False),
                Task(title="Build a REST API", done=False),
                Task(title="Deploy to production", done=True),
            ]
            session.add_all(seed_tasks)
            session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Task API",
    version="2.0.0",
    description="A simple task management API with SQLite persistence",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get(
    "/",
    summary="Root endpoint",
    description="Returns API metadata and available endpoints"
)
async def root():
    return {
        "name": "Task API",
        "version": "2.0.0",
        "endpoints": ["/tasks", "/tasks/{task_id}", "/stats"]
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
):
    with Session(engine) as session:
        query = select(Task)

        if search:
            query = query.where(Task.title.ilike(f"%{search}%"))

        if done is not None:
            query = query.where(Task.done == done)

        if sort:
            if sort == "title":
                query = query.order_by(Task.title.asc())
            elif sort == "-title":
                query = query.order_by(Task.title.desc())

        tasks = session.exec(query).all()
        return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=TaskRead,
    summary="Get a single task",
    description="Returns a task by its ID"
)
async def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
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
async def create_task(task_data: TaskCreate):
    with Session(engine) as session:
        task = Task(title=task_data.title, done=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@app.put(
    "/tasks/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Updates a task by ID. Can update title and/or done status."
)
async def update_task(task_id: int, task_data: TaskUpdate):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "Task not found"}
            )

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.done is not None:
            task.done = task_data.done

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Deletes a task by ID"
)
async def delete_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "Task not found"}
            )
        session.delete(task)
        session.commit()


@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get task statistics",
    description="Returns counts of total, completed, and pending tasks"
)
async def get_stats():
    with Session(engine) as session:
        total = session.exec(select(Task)).all()
        total_count = len(total)
        completed = session.exec(select(Task).where(Task.done == True)).all()
        completed_count = len(completed)
        return StatsResponse(
            total=total_count,
            completed=completed_count,
            pending=total_count - completed_count
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)