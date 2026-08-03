from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.dependencies import get_current_user
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
async def protected_profile(user: dict = Depends(get_current_user)):
    return ProtectedProfileResponse(
        id=user["id"],
        email=user["email"],
        created_at=user["created_at"]
    )


@router.get(
    "/protected/dashboard",
    response_model=ProtectedProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get protected dashboard",
    description="Second protected route using the same auth middleware",
    responses={
        200: {"description": "Dashboard data returned with verified user data"},
        401: {"model": ErrorResponse, "description": "Access token required or invalid/expired"},
    },
)
async def protected_dashboard(user: dict = Depends(get_current_user)):
    return ProtectedProfileResponse(
        id=user["id"],
        email=user["email"],
        created_at=user["created_at"]
    )