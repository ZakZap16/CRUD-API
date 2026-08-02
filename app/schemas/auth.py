from pydantic import BaseModel, EmailStr


class AuthSignupRequest(BaseModel):
    email: EmailStr
    password: str


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


class UserProfile(BaseModel):
    id: str
    email: str
    created_at: str


class PublicInfoResponse(BaseModel):
    message: str


class ProtectedProfileResponse(BaseModel):
    id: str
    email: str
    created_at: str


class ErrorResponse(BaseModel):
    error: str