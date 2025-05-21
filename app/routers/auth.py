import random
from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
import secrets
import bcrypt
import datetime
from pydantic import BaseModel, EmailStr, constr
from jose import jwt

from app.routers.util import get_verified_user_email
from app.services.email import send_reset_password_email, send_verify_email
from app.config import Config


from app.database.connection import (
    confirm_user, create_user, delete_otp, get_public_user_by_email, get_user_by_email, update_user_password,
    create_session, delete_session, create_otp, verify_otp
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

class UserConfirm(BaseModel):
    email: EmailStr
    code: str

class UserResponse(UserBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime.datetime

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str


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

def get_cookie_dict(token: str):
    return {
        "key": "Authorization",
        "value": f"Bearer {token}",
        "httponly": True,
        "secure": config.environment != "development",
        "samesite": "lax",
        "max_age": 7 * 24 * 60 * 60
    }


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
    token = jwt.encode(
        {"sub": user_data.email, "exp": datetime.datetime.now() + datetime.timedelta(days=7)},
        config.session_secret_key,
        algorithm="HS256",
    )

    response = Response(status_code=200)
    response.set_cookie(
        **get_cookie_dict(token)
    )

    return response

@router.post("/confirm-email")
async def confirm_email(data: UserConfirm):
    # Get unique token from database
    user = get_user_by_email(data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error confirming email"
        )
    
    if not verify_otp(user['id'], data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code"
        )
    
    if user['confirmed']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already confirmed"
        )
    
    confirm_user(user['id'])
    delete_otp(user['id'], data.code)

    token = jwt.encode(
        {"sub": data.email, "exp": datetime.datetime.now() + datetime.timedelta(days=7)},
        config.session_secret_key,
        algorithm="HS256",
    )

    response = Response(status_code=200)
    response.set_cookie(
        **get_cookie_dict(token)
    )

    return response

@router.get("/logout", response_model=MessageResponse)
async def logout_user():
    """Log out a user"""
    response = Response(status_code=200)
    response.set_cookie(
        "Authorization",
        path="/",
        httponly=True,
        secure=config.environment != "development",
        samesite="lax",
        max_age=0
    )

    return response

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
    unique_token = ''.join(random.choices('0123456789', k=6))
    create_otp(user_id, unique_token)

    # Send email with unique token
    send_verify_email(user_data.email, unique_token, config)

    return MessageResponse(detail="Successfully registered")

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload:ForgotPasswordRequest):
    """Initiate password reset"""
    # Get user from database
    user = get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Generate reset token
    reset_token = ''.join(random.choices('0123456789', k=6))
    create_otp(user["id"], reset_token)
    
    # Store reset token in database
    send_reset_password_email(payload.email, reset_token, config)

    return MessageResponse(
        detail="Password reset initiated! Please check your email for instructions."
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_password_request: ResetPasswordRequest
):
    """Complete password reset"""
    # Validate passwords match
    if reset_password_request.new_password != reset_password_request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password meets requirements
    is_valid, error_message = validate_password(reset_password_request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Get user from database
    user = get_user_by_email(reset_password_request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Verify reset token
    if not verify_otp(user["id"], reset_password_request.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Hash new password
    password_hash = hash_password(reset_password_request.new_password)
    
    # Update password
    update_user_password(user["id"], password_hash)

    delete_otp(user["id"], reset_password_request.otp)
    
    return MessageResponse(
        detail="Password reset successful! You can now log in with your new password."
    )

@router.get("/me", response_model=UserBase)
async def get_me(user_email: str = Depends(get_verified_user_email)):
    """Get the current user"""
    user = get_public_user_by_email(user_email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return UserBase.model_validate(user)

