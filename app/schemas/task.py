from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    done: Optional[bool] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool
    created_at: datetime
    updated_at: datetime


class StatsResponse(BaseModel):
    total: int
    completed: int
    pending: int