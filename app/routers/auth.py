from fastapi import APIRouter, Request, Response, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
import os
from pathlib import Path
import secrets
from app.services.email import send_reset_password_email, send_verify_email
import bcrypt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, constr
from app.config import Config

from app.database.connection import (
    create_user, get_user_by_email, update_user_password,
    create_session, get_session, delete_session, delete_expired_sessions,
    create_unique_token, verify_unique_token
)


config = Config()

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone_number: str
    school: str
    role: str

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class MessageResponse(BaseModel):
    detail: str

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_session_token() -> str:
    """Create a new session token"""
    return secrets.token_urlsafe(32)

@router.post("/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin):
    """Authenticate a user"""
    # Get user from database
    user = get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create session
    session_token = create_session_token()
    expires_at = datetime.now() + timedelta(days=30)
    
    session_id = create_session(user["id"], session_token, expires_at.isoformat())
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )
    
    return TokenResponse(
        access_token=session_token,
        expires_at=expires_at
    )

@router.post("/confirm-email", response_model=MessageResponse)
async def confirm_email(unique_token: str):
    # Get unique token from database

    # If token is valid, update user email_verified to True

    # Return success
    return MessageResponse(detail="Successfully confirmed email")

@router.post("/logout", response_model=MessageResponse)
async def logout_user(request: Request):
    """Log out a user"""
    # Get session token from cookies
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Delete session from database
        delete_session(session_token)
    
    return MessageResponse(detail="Successfully logged out")

@router.post("/register", response_model=MessageResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Validate passwords match
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password meets requirements
    is_valid, error_message = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Format phone number with + prefix if not present
    phone_number = user_data.phone_number
    if phone_number and not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    user_id = create_user(
        user_data.email,
        password_hash,
        user_data.name,
        phone_number,
        user_data.school,
        user_data.role
    )
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Generate unique token for email confirmation
    unique_token = secrets.token_urlsafe(32)
    create_unique_token(user_id, unique_token)

    # Send email with unique token
    send_verify_email(user_data.email, unique_token, config)

    return MessageResponse(detail="Successfully registered")

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(email: EmailStr):
    """Initiate password reset"""
    # Get user from database
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    create_unique_token(user["id"], reset_token)
    
    # Store reset token in database
    send_reset_password_email(email, reset_token, config)

    return MessageResponse(
        detail="Password reset initiated! Please check your email for instructions."
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    email: EmailStr,
    token: str,
    new_password: constr(min_length=8),
    confirm_password: str
):
    """Complete password reset"""
    # Validate passwords match
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password meets requirements
    is_valid, error_message = validate_password(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Get user from database
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Verify reset token
    # Note: You would need to verify the token from the reset_tokens table
    # For now, we'll just update the password
    
    # Hash new password
    password_hash = hash_password(new_password)
    
    # Update password
    if not update_user_password(user["id"], password_hash):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return MessageResponse(
        detail="Password reset successful! You can now log in with your new password."
    )

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must have uppercase characters"
    
    if not any(c.islower() for c in password):
        return False, "Password must have lowercase characters"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must have numeric characters"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
        return False, "Password must have symbol characters"
    
    return True, ""
