from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.auth.supabase_client import supabase
from app.dependencies import get_current_user
from app.schemas.auth import (
    AuthSignupRequest,
    AuthLoginRequest,
    AuthResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up a new user",
    description="Creates a new user account with email and password",
    responses={
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse, "description": "Missing email or password"},
    },
)
async def signup(request: AuthSignupRequest):
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    response = supabase.auth.sign_up({
        "email": request.email,
        "password": request.password,
    })

    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user",
        )

    return AuthResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        user={
            "id": response.user.id,
            "email": response.user.email,
            "created_at": response.user.created_at,
        },
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in a user",
    description="Authenticates a user and returns access and refresh tokens",
    responses={
        200: {"description": "Login successful"},
        400: {"model": ErrorResponse, "description": "Missing email or password"},
        401: {"model": ErrorResponse, "description": "Invalid login credentials"},
    },
)
async def login(request: AuthLoginRequest):
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    response = supabase.auth.sign_in_with_password({
        "email": request.email,
        "password": request.password,
    })

    if response.user is None or response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
        )

    return AuthResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        user={
            "id": response.user.id,
            "email": response.user.email,
            "created_at": response.user.created_at,
        },
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out a user",
    description="Ends the user's session (requires valid access token)",
    responses={
        204: {"description": "Logged out successfully"},
        401: {"model": ErrorResponse, "description": "Access token required or invalid/expired"},
    },
)
async def logout(user: dict = Depends(get_current_user)):
    supabase.auth.sign_out()
    return None