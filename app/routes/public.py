from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional

from app.auth.supabase_client import supabase
from app.schemas.auth import (
    PublicInfoResponse,
    ProtectedProfileResponse,
    ErrorResponse,
)

router = APIRouter(tags=["Public"])


@router.get(
    "/public/info",
    response_model=PublicInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get public info",
    description="Returns a public message - no authentication required",
    responses={
        200: {"description": "Public info returned successfully"},
    },
)
async def public_info():
    return PublicInfoResponse(message="Welcome stranger! This info is public.")


@router.get(
    "/protected/profile",
    response_model=ProtectedProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get protected profile (token verified with Supabase)",
    description="Verifies the JWT token with Supabase and returns user profile",
    responses={
        200: {"description": "Profile returned with verified user data"},
        401: {"model": ErrorResponse, "description": "Access token required or invalid/expired"},
    },
)
async def protected_profile(authorization: Optional[str] = Header(None)):
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
    return ProtectedProfileResponse(
        id=user.id,
        email=user.email,
        created_at=str(user.created_at)
    )