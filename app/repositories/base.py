from abc import ABC, abstractmethod
from typing import List, Optional
from sqlmodel import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, StatsResponse


class TaskRepository(ABC):
    """Abstract interface for task storage. Implementations must provide all CRUD operations."""

    @abstractmethod
    def get_all(
        self,
        db: Session,
        search: Optional[str] = None,
        done: Optional[bool] = None,
        sort: Optional[str] = None,
    ) -> List[TaskRead]:
        """Get all tasks with optional filtering and sorting."""
        pass

    @abstractmethod
    def get_by_id(self, db: Session, task_id: int) -> Optional[TaskRead]:
        """Get a single task by ID."""
        pass

    @abstractmethod
    def create(self, db: Session, task_data: TaskCreate) -> TaskRead:
        """Create a new task."""
        pass

    @abstractmethod
    def update(self, db: Session, task_id: int, task_data: TaskUpdate) -> Optional[TaskRead]:
        """Update a task by ID."""
        pass

    @abstractmethod
    def delete(self, db: Session, task_id: int) -> bool:
        """Delete a task by ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def get_stats(self, db: Session) -> StatsResponse:
        """Get task statistics."""
        pass

    @abstractmethod
    def seed_if_empty(self, db: Session) -> None:
        """Insert seed data if table is empty."""
        pass