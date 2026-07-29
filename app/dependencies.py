from typing import Generator
from fastapi import Depends
from sqlmodel import Session

from app.database import get_session
from app.repositories.base import TaskRepository
from app.repositories.sqlite import SQLiteTaskRepository
from app.repositories.postgres import PostgresTaskRepository
import os


def get_task_repository(db: Session = Depends(get_session)) -> TaskRepository:
    database_url = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    if database_url.startswith("postgresql"):
        return PostgresTaskRepository()
    return SQLiteTaskRepository()