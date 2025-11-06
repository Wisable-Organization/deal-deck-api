"""
Authentication routes for login, register, and password reset
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta
import os
import re

from .auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    generate_password_reset_token,
    get_current_user_id,
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS
)
# Get storage instance
def get_storage():
    """Get storage instance"""
    try:
        from .storage import Storage
        storage = Storage()
        return storage
    except Exception:
        from .memory_storage import MemoryStorage
        return MemoryStorage()

storage = get_storage()
router = APIRouter()
security = HTTPBearer()


def validate_email(email: str) -> str:
    """Manually validate email format"""
    if not email or not isinstance(email, str):
        raise ValueError("Email must be a non-empty string")
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    
    # Additional checks
    if len(email) > 255:
        raise ValueError("Email is too long (max 255 characters)")
    
    if email.count('@') != 1:
        raise ValueError("Email must contain exactly one @ symbol")
    
    local, domain = email.split('@')
    
    if not local or len(local) > 64:
        raise ValueError("Email local part is invalid")
    
    if not domain or '.' not in domain:
        raise ValueError("Email domain is invalid")
    
    return email


# Request/Response models
class LoginRequest(BaseModel):
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_email(v)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_email(v)


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    message: str


class PasswordResetRequest(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_email(v)


class PasswordResetResponse(BaseModel):
    message: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordResetConfirmResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: str
    email: str
    email_confirmed_at: Optional[datetime] = None
    created_at: datetime


# Routes
@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user"""
    # Check if user already exists
    existing_user = await storage.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(request.password)
    user = await storage.create_user(request.email, hashed_password)
    
    return RegisterResponse(
        user_id=user["id"],
        email=user["email"],
        message="User registered successfully"
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login and get JWT token"""
    # Get user by email
    user = await storage.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user["encrypted_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user["id"],
        email=user["email"]
    )


@router.post("/password-reset-request", response_model=PasswordResetResponse)
async def password_reset_request(request: PasswordResetRequest):
    """Request password reset - generates token and stores it"""
    # Get user by email
    user = await storage.get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return PasswordResetResponse(
            message="If the email exists, a password reset link has been sent"
        )
    
    # Generate reset token
    reset_token = generate_password_reset_token()
    
    # Store token in database
    await storage.set_recovery_token(user["id"], reset_token)
    
    # In production, send email with reset link
    # For now, we'll just return success
    # The frontend will need to handle the token from the URL
    reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={reset_token}"
    
    # TODO: Send email with reset_link
    # For development, you might want to log this:
    print(f"Password reset link for {request.email}: {reset_link}")
    
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/password-reset-confirm", response_model=PasswordResetConfirmResponse)
async def password_reset_confirm(request: PasswordResetConfirm):
    """Confirm password reset with token"""
    # Get user by recovery token
    user = await storage.get_user_by_recovery_token(request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired (24 hours)
    if user["recovery_sent_at"]:
        token_age = datetime.utcnow() - user["recovery_sent_at"]
        if token_age > timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
    
    # Update password
    hashed_password = get_password_hash(request.new_password)
    success = await storage.update_user_password(user["id"], hashed_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return PasswordResetConfirmResponse(
        message="Password has been reset successfully"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current authenticated user"""
    user = await storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        email_confirmed_at=user["email_confirmed_at"],
        created_at=user["created_at"]
    )

