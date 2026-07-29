from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import func

from app.repositories.base import TaskRepository
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, StatsResponse


class SQLiteTaskRepository(TaskRepository):
    """SQLite implementation of TaskRepository."""

    def get_all(
        self,
        db: Session,
        search: Optional[str] = None,
        done: Optional[bool] = None,
        sort: Optional[str] = None,
    ) -> List[TaskRead]:
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

        tasks = db.exec(query).all()
        return [TaskRead.model_validate(task) for task in tasks]

    def get_by_id(self, db: Session, task_id: int) -> Optional[TaskRead]:
        task = db.get(Task, task_id)
        if not task:
            return None
        return TaskRead.model_validate(task)

    def create(self, db: Session, task_data: TaskCreate) -> TaskRead:
        task = Task(title=task_data.title, done=False)
        db.add(task)
        db.commit()
        db.refresh(task)
        return TaskRead.model_validate(task)

    def update(self, db: Session, task_id: int, task_data: TaskUpdate) -> Optional[TaskRead]:
        task = db.get(Task, task_id)
        if not task:
            return None

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.done is not None:
            task.done = task_data.done

        task.updated_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)
        return TaskRead.model_validate(task)

    def delete(self, db: Session, task_id: int) -> bool:
        task = db.get(Task, task_id)
        if not task:
            return False
        db.delete(task)
        db.commit()
        return True

    def get_stats(self, db: Session) -> StatsResponse:
        total = db.exec(select(func.count(Task.id))).one()
        completed = db.exec(select(func.count(Task.id)).where(Task.done == True)).one()
        return StatsResponse(total=total, completed=completed, pending=total - completed)

    def seed_if_empty(self, db: Session) -> None:
        count = db.exec(select(func.count(Task.id))).one()
        if count == 0:
            seed_tasks = [
                Task(title="Learn FastAPI", done=False),
                Task(title="Build a REST API", done=False),
                Task(title="Deploy to production", done=True),
            ]
            db.add_all(seed_tasks)
            db.commit()