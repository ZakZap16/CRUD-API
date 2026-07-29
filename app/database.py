import os
from contextlib import contextmanager
from typing import Generator
from sqlmodel import create_engine, Session

from app.config import get_settings

settings = get_settings()
DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session"""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    from app.models.task import Task
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)