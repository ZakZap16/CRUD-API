from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional

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
    summary="Get protected profile (token presence check only)",
    description="Checks for Authorization: Bearer <token> header but does not verify token yet",
    responses={
        200: {"description": "Profile returned (token verification happens in Stage 3)"},
        401: {"model": ErrorResponse, "description": "Access token required"},
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
    
    return ProtectedProfileResponse(
        id="pending-verification",
        email="pending-verification",
        created_at="pending-verification"
    )