from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from sqlmodel import Session

from app.database import get_session
from app.repositories.base import TaskRepository
from app.repositories.sqlite import SQLiteTaskRepository
from app.repositories.postgres import PostgresTaskRepository
from app.auth.supabase_client import supabase
import os


def get_task_repository(db: Session = Depends(get_session)) -> TaskRepository:
    database_url = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    if database_url.startswith("postgresql"):
        return PostgresTaskRepository()
    return SQLiteTaskRepository()


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Extract and verify JWT token from Authorization header, return user data."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )
    
    # Verify token with Supabase
    try:
        user_response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    if user_response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user = user_response.user
    return {
        "id": user.id,
        "email": user.email,
        "created_at": str(user.created_at)
    }