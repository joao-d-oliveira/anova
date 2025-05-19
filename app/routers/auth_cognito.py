from fastapi import APIRouter, Request, Response, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from pathlib import Path

from services.cognito import (
    register_user, confirm_registration, login, logout,
    forgot_password, confirm_forgot_password, verify_token,
    cognito_idp
)
from database.connection import execute_query

# Set up Jinja2 templates
root = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(root, "../templates"))

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """
    Display the login page
    """
    context = {"request": request}
    
    # Handle specific error messages
    if error == "auth_service_unavailable":
        context["error"] = "Authentication service is unavailable. Please contact the administrator."
    elif error:
        context["error"] = error
        
    return templates.TemplateResponse("auth/login.html", context)

@router.post("/login")
async def login_user(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Authenticate a user
    """
    print(f"Login route called for email: {email}")
    
    # For development mode, bypass authentication if requested
    if os.getenv("ENVIRONMENT", "development") == "development" and email == "dev@example.com" and password == "dev":
        print("Using development mode authentication bypass")
        
        # Create a mock response with redirect
        redirect_response = RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)
        
        # Set mock cookies for authentication
        max_age = 3600  # 1 hour
        redirect_response.set_cookie(
            key="access_token", 
            value="mock_access_token",
            httponly=True,
            max_age=max_age,
            path="/"
        )
        
        redirect_response.set_cookie(
            key="id_token", 
            value="mock_id_token",
            httponly=True,
            max_age=max_age,
            path="/"
        )
        
        redirect_response.set_cookie(
            key="refresh_token", 
            value="mock_refresh_token",
            httponly=True,
            max_age=30 * 24 * 3600,  # 30 days
            path="/"
        )
        
        # Return the redirect response
        return redirect_response
    
    # Check if Cognito is properly configured
    if not os.getenv("COGNITO_CLIENT_SECRET"):
        # If we're in development mode and Cognito is not configured, use a mock user
        if os.getenv("ENVIRONMENT", "development") == "development":
            print("WARNING: COGNITO_CLIENT_SECRET is not set. Using mock authentication in development mode.")
            
            # Create a mock response with redirect
            redirect_response = RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)
            
            # Set mock cookies for authentication
            max_age = 3600  # 1 hour
            redirect_response.set_cookie(
                key="access_token", 
                value="mock_access_token",
                httponly=True,
                max_age=max_age,
                path="/"
            )
            
            redirect_response.set_cookie(
                key="id_token", 
                value="mock_id_token",
                httponly=True,
                max_age=max_age,
                path="/"
            )
            
            redirect_response.set_cookie(
                key="refresh_token", 
                value="mock_refresh_token",
                httponly=True,
                max_age=30 * 24 * 3600,  # 30 days
                path="/"
            )
            
            # Return the redirect response
            return redirect_response
        else:
            # In production, show an error
            return templates.TemplateResponse(
                "auth/login.html", 
                {
                    "request": request,
                    "error": "Authentication service is not properly configured. Please contact the administrator."
                }
            )
    
    try:
        # Authenticate with Cognito
        print("Calling login function...")
        auth_result = login(email, password)
        print(f"Login successful, got auth result with keys: {auth_result.keys()}")
        
        # Get user info from token
        user_info = verify_token(auth_result["IdToken"])
        
        # Check if user exists in our database
        query = "SELECT id FROM users WHERE cognito_id = %s"
        result = execute_query(query, (user_info.get("sub"),))
        
        if not result:
            # User doesn't exist in our database, create them
            insert_query = """
            INSERT INTO users (cognito_id, email, name, phone_number, school, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            # Extract custom attributes
            phone_number = user_info.get("phone_number", "")
            school = user_info.get("custom:school", "")
            role = user_info.get("custom:role", "")
            
            execute_query(
                insert_query, 
                (
                    user_info.get("sub"),
                    user_info.get("email"),
                    user_info.get("name"),
                    phone_number,
                    school,
                    role
                ),
                fetch=False
            )
        
        # Create a response with redirect
        redirect_response = RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)
        
        # Set cookies for authentication
        max_age = 3600  # 1 hour
        redirect_response.set_cookie(
            key="access_token", 
            value=auth_result["AccessToken"],
            httponly=True,
            max_age=max_age,
            path="/"
        )
        
        redirect_response.set_cookie(
            key="id_token", 
            value=auth_result["IdToken"],
            httponly=True,
            max_age=max_age,
            path="/"
        )
        
        redirect_response.set_cookie(
            key="refresh_token", 
            value=auth_result["RefreshToken"],
            httponly=True,
            max_age=30 * 24 * 3600,  # 30 days
            path="/"
        )
        
        # Return the redirect response
        return redirect_response
    except Exception as e:
        error_str = str(e)
        
        # Check if this is a UserNotConfirmedException
        if "UserNotConfirmedException" in error_str:
            # Redirect to confirmation page with message
            return templates.TemplateResponse(
                "auth/confirm.html", 
                {
                    "request": request,
                    "email": email,
                    "message": "Your account needs to be confirmed before logging in. Please check your email for a confirmation code."
                }
            )
        
        # Return to login page with error for other exceptions
        return templates.TemplateResponse(
            "auth/login.html", 
            {
                "request": request,
                "error": f"Login failed: {error_str}"
            }
        )

@router.get("/logout")
async def logout_user(request: Request):
    """
    Log out a user
    """
    try:
        # Get access token from cookies
        access_token = request.cookies.get("access_token")
        
        if access_token:
            # Logout from Cognito
            logout(access_token)
        
        # Create response with redirect
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
        # Clear cookies
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="id_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        
        return response
    except Exception as e:
        # Redirect to landing page anyway
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
        # Clear cookies
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="id_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        
        return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    Display the registration page
    """
    return templates.TemplateResponse("auth/register.html", {"request": request})

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password against Cognito password policy
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase
    if not any(c.isupper() for c in password):
        return False, "Password must have uppercase characters"
    
    # Check for lowercase
    if not any(c.islower() for c in password):
        return False, "Password must have lowercase characters"
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        return False, "Password must have numeric characters"
    
    # Check for symbols
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
        return False, "Password must have symbol characters"
    
    return True, ""

@router.post("/register")
async def register_user_route(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    school: str = Form(...),
    role: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """
    Register a new user
    """
    try:
        # Validate passwords match
        if password != confirm_password:
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": "Passwords do not match",
                    "name": name,
                    "email": email,
                    "phone_number": phone_number,
                    "school": school,
                    "role": role
                }
            )
        
        # Validate password meets requirements
        is_valid, error_message = validate_password(password)
        if not is_valid:
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request,
                    "error": error_message,
                    "name": name,
                    "email": email,
                    "phone_number": phone_number,
                    "school": school,
                    "role": role
                }
            )
        
        # Format phone number with + prefix if not present
        if not phone_number.startswith('+'):
            phone_number = f"+{phone_number}"
        
        # Register with Cognito
        register_response = register_user(email, password, name, phone_number, school, role)
        
        # Auto-confirm the user in development environment
        if os.getenv("ENVIRONMENT", "development") == "development":
            try:
                # Create a new boto3 client with AWS credentials
                import boto3
                client = boto3.client(
                    'cognito-idp',
                    region_name=os.getenv("AWS_REGION", "us-east-1"),
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                )
                
                # Use Cognito admin API to confirm the user
                client.admin_confirm_sign_up(
                    UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                    Username=email
                )
                
                # Also mark the email as verified
                client.admin_update_user_attributes(
                    UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                    Username=email,
                    UserAttributes=[
                        {
                            'Name': 'email_verified',
                            'Value': 'true'
                        }
                    ]
                )
                
                # Redirect to login page with success message
                return templates.TemplateResponse(
                    "auth/login.html", 
                    {
                        "request": request,
                        "email": email,
                        "message": "Registration successful! Your account has been automatically confirmed. You can now log in."
                    }
                )
            except Exception as e:
                # If auto-confirmation fails, fall back to manual confirmation
                return templates.TemplateResponse(
                    "auth/confirm.html", 
                    {
                        "request": request,
                        "email": email,
                        "message": f"Registration successful, but auto-confirmation failed: {str(e)}. Please check your email for a confirmation code or use the developer tool to confirm your account."
                    }
                )
        else:
            # In production, redirect to confirmation page
            return templates.TemplateResponse(
                "auth/confirm.html", 
                {
                    "request": request,
                    "email": email,
                    "message": "Registration successful! Please check your email for a confirmation code."
                }
            )
    except Exception as e:
        # Return to registration page with error
        return templates.TemplateResponse(
            "auth/register.html", 
            {
                "request": request,
                "error": f"Registration failed: {str(e)}",
                "name": name,
                "email": email,
                "phone_number": phone_number,
                "school": school,
                "role": role
            }
        )

@router.get("/confirm", response_class=HTMLResponse)
async def confirm_page(request: Request, email: Optional[str] = None):
    """
    Display the confirmation page
    """
    return templates.TemplateResponse(
        "auth/confirm.html", 
        {
            "request": request,
            "email": email
        }
    )

@router.post("/confirm")
async def confirm_registration_route(
    request: Request,
    email: str = Form(...),
    code: str = Form(...)
):
    """
    Confirm user registration
    """
    try:
        # Confirm registration with Cognito
        confirm_registration(email, code)
        
        # Redirect to login page
        return templates.TemplateResponse(
            "auth/login.html", 
            {
                "request": request,
                "message": "Email confirmed! You can now log in.",
                "email": email
            }
        )
    except Exception as e:
        # Return to confirmation page with error
        return templates.TemplateResponse(
            "auth/confirm.html", 
            {
                "request": request,
                "error": f"Confirmation failed: {str(e)}",
                "email": email
            }
        )

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """
    Display the forgot password page
    """
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request})

@router.post("/forgot-password")
async def forgot_password_route(
    request: Request,
    email: str = Form(...)
):
    """
    Initiate password reset
    """
    try:
        # In development environment, ensure email is verified first
        if os.getenv("ENVIRONMENT", "development") == "development":
            try:
                # Create a new boto3 client with AWS credentials
                import boto3
                client = boto3.client(
                    'cognito-idp',
                    region_name=os.getenv("AWS_REGION", "us-east-1"),
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                )
                
                # Mark the email as verified
                client.admin_update_user_attributes(
                    UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                    Username=email,
                    UserAttributes=[
                        {
                            'Name': 'email_verified',
                            'Value': 'true'
                        }
                    ]
                )
            except Exception as e:
                # If verification fails, log the error but continue
                print(f"Failed to verify email before password reset: {str(e)}")
        
        # Initiate password reset with Cognito
        forgot_password(email)
        
        # Redirect to reset password page
        return templates.TemplateResponse(
            "auth/reset_password.html", 
            {
                "request": request,
                "email": email,
                "message": "Password reset initiated! Please check your email for a confirmation code."
            }
        )
    except Exception as e:
        # Return to forgot password page with error
        return templates.TemplateResponse(
            "auth/forgot_password.html", 
            {
                "request": request,
                "error": f"Password reset failed: {str(e)}",
                "email": email
            }
        )

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, email: Optional[str] = None):
    """
    Display the reset password page
    """
    return templates.TemplateResponse(
        "auth/reset_password.html", 
        {
            "request": request,
            "email": email
        }
    )

@router.post("/reset-password")
async def reset_password_route(
    request: Request,
    email: str = Form(...),
    code: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """
    Complete password reset
    """
    try:
        # Validate passwords match
        if new_password != confirm_password:
            return templates.TemplateResponse(
                "auth/reset_password.html", 
                {
                    "request": request,
                    "error": "Passwords do not match",
                    "email": email
                }
            )
        
        # Complete password reset with Cognito
        confirm_forgot_password(email, code, new_password)
        
        # Redirect to login page
        return templates.TemplateResponse(
            "auth/login.html", 
            {
                "request": request,
                "message": "Password reset successful! You can now log in with your new password.",
                "email": email
            }
        )
    except Exception as e:
        # Return to reset password page with error
        return templates.TemplateResponse(
            "auth/reset_password.html", 
            {
                "request": request,
                "error": f"Password reset failed: {str(e)}",
                "email": email
            }
        )

@router.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """
    Display the terms and conditions page
    """
    return templates.TemplateResponse("auth/terms.html", {"request": request})

@router.post("/terms")
async def terms_agree(request: Request):
    """
    Handle terms agreement submission
    """
    # Redirect back to registration page
    return RedirectResponse(url="/auth/register", status_code=status.HTTP_302_FOUND)

# Development-only endpoints
if os.getenv("ENVIRONMENT", "development") == "development":
    @router.get("/dev/confirm")
    async def dev_confirm_page(request: Request):
        """
        Development-only page to manually confirm users
        """
        return templates.TemplateResponse("auth/dev_confirm.html", {"request": request})
        
    @router.get("/dev/confirm-user/{email}")
    async def confirm_user_dev(request: Request, email: str):
        """
        Development-only endpoint to manually confirm a user's registration
        """
        try:
            # Create a new boto3 client with AWS credentials
            import boto3
            client = boto3.client(
                'cognito-idp',
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            # Use Cognito admin API to confirm the user
            client.admin_confirm_sign_up(
                UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                Username=email
            )
            
            # Also mark the email as verified
            client.admin_update_user_attributes(
                UserPoolId=os.getenv("COGNITO_USER_POOL_ID"),
                Username=email,
                UserAttributes=[
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ]
            )
            
            return {
                "status": "success",
                "message": f"User {email} has been confirmed. You can now log in."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to confirm user: {str(e)}"
            }
