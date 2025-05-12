from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Optional
import logging
import os
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.services.cognito import verify_token, refresh_token, cognito_public_keys

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication for protected routes
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Check if Cognito is properly configured
        self.cognito_available = bool(cognito_public_keys)
        if not self.cognito_available:
            logger.warning("Cognito authentication is not available. Running in limited functionality mode.")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and enforce authentication
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response from the next middleware or route handler
        """
        # Skip authentication for landing page
        if request.url.path == "/":
            logger.debug(f"Skipping auth for path: {request.url.path}")
            return await call_next(request)
            
        # Skip authentication for auth-related endpoints
        if request.url.path.startswith("/auth/"):
            logger.debug(f"Skipping auth for auth path: {request.url.path}")
            return await call_next(request)
            
        # Skip authentication for static files
        if request.url.path.startswith("/static/"):
            logger.debug(f"Skipping auth for static path: {request.url.path}")
            return await call_next(request)
            
        # If Cognito is not available, bypass authentication
        if not self.cognito_available:
            logger.warning(f"Bypassing authentication for path: {request.url.path} (Cognito unavailable)")
            # Set a mock user for development purposes
            request.state.user = {
                "email": "dev@example.com",
                "name": "Development User",
                "sub": "dev-user-id"
            }
            return await call_next(request)
            
        # Check for token in cookies
        try:
            logger.debug(f"Checking auth for path: {request.url.path}")
            
            # Get tokens directly from cookies
            id_token = request.cookies.get("id_token")
            access_token = request.cookies.get("access_token")
            refresh_token_str = request.cookies.get("refresh_token")
                
            logger.debug(f"Cookie tokens - Access: {'Present' if access_token else 'Missing'}, ID: {'Present' if id_token else 'Missing'}, Refresh: {'Present' if refresh_token_str else 'Missing'}")
        except Exception as e:
            # If there's any issue with the cookies, redirect to login page
            logger.error(f"Cookie error: {str(e)}")
            return RedirectResponse(url="/auth/login")
        
        if not id_token:
            # Redirect to login page
            logger.debug("No ID token found in cookies, redirecting to login")
            return RedirectResponse(url="/auth/login")
            
        # Verify token
        try:
            logger.debug("Verifying ID token")
            user = verify_token(id_token)
            logger.debug(f"Token verified successfully for user: {user.get('email')}")
            # Add user to request state
            request.state.user = user
            return await call_next(request)
        except Exception as e:
            # Token is invalid, try to refresh
            logger.error(f"Token verification failed: {str(e)}")
            if refresh_token_str:
                try:
                    # Refresh the token
                    logger.debug("Attempting to refresh token")
                    auth_result = refresh_token(refresh_token_str)
                    logger.debug("Token refreshed successfully")
                    
                    # Create response to update cookies
                    response = await call_next(request)
                    
                    # Set new tokens in cookies
                    max_age = 3600  # 1 hour
                    response.set_cookie(
                        key="access_token", 
                        value=auth_result["AccessToken"],
                        httponly=True,
                        max_age=max_age,
                        path="/"
                    )
                    response.set_cookie(
                        key="id_token", 
                        value=auth_result["IdToken"],
                        httponly=True,
                        max_age=max_age,
                        path="/"
                    )
                    response.set_cookie(
                        key="refresh_token", 
                        value=auth_result["RefreshToken"],
                        httponly=True,
                        max_age=30 * 24 * 3600,  # 30 days
                        path="/"
                    )
                    
                    logger.debug("Updated tokens in cookies")
                    
                    return response
                except Exception as refresh_error:
                    # Refresh failed, redirect to login
                    logger.error(f"Token refresh failed: {str(refresh_error)}")
                    response = RedirectResponse(url="/auth/login")
                    response.delete_cookie("access_token")
                    response.delete_cookie("id_token")
                    response.delete_cookie("refresh_token")
                    return response
            else:
                # No refresh token, redirect to login
                logger.debug("No refresh token available, redirecting to login")
                response = RedirectResponse(url="/auth/login")
                response.delete_cookie("access_token")
                response.delete_cookie("id_token")
                response.delete_cookie("refresh_token")
                return response

def get_current_user(request: Request) -> Optional[dict]:
    """
    Get the current authenticated user from the request state
    
    Args:
        request: The incoming request
        
    Returns:
        Dict containing user information or None if not authenticated
    """
    return getattr(request.state, "user", None)
