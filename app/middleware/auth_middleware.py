from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Optional
import logging
import os
import json
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.cognito import verify_token, refresh_token, cognito_public_keys

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication for protected routes
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Check if Cognito is properly configured
        self.cognito_available = bool(cognito_public_keys)
        if not self.cognito_available:
            logger.error("Cognito authentication is not available. Authentication will be restricted.")
        
        # Log the working directory for debugging
        logger.info(f"AuthMiddleware initialized. Working directory: {os.getcwd()}")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and enforce authentication
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response from the next middleware or route handler
        """
        # Generate a request ID for tracing
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Get the full URL and path for logging
        full_url = str(request.url)
        path = request.url.path
        
        logger.info(f"[{request_id}] Request received: {request.method} {full_url}")
        logger.info(f"[{request_id}] Path being processed: '{path}'")
        logger.info(f"[{request_id}] Client host: {request.client.host if request.client else 'unknown'}")
        
        # Log cookies (excluding sensitive data)
        cookie_keys = list(request.cookies.keys())
        logger.info(f"[{request_id}] Cookies present: {cookie_keys}")
        
        # Skip authentication for landing page
        if path == "/":
            logger.info(f"[{request_id}] Skipping auth for root path '/'")
            return await call_next(request)
            
        # Skip authentication for auth-related endpoints
        if path.startswith("/auth/"):
            logger.info(f"[{request_id}] Skipping auth for auth path: '{path}'")
            return await call_next(request)
            
        # Skip authentication for static files
        if path.startswith("/static/"):
            logger.info(f"[{request_id}] Skipping auth for static path: '{path}'")
            return await call_next(request)
            
        # If Cognito is not available
        if not self.cognito_available:
            # Only allow access to landing page, static files, and maintenance page
            if path == "/" or path.startswith("/static/") or path == "/maintenance":
                logger.warning(f"[{request_id}] Allowing access to essential path despite Cognito being unavailable: '{path}'")
                return await call_next(request)
            else:
                # For all other paths, redirect to the maintenance page
                logger.error(f"[{request_id}] Redirecting '{path}' to maintenance page - Cognito authentication is unavailable")
                return RedirectResponse(url="/maintenance")
            
        # Check for token in cookies
        try:
            logger.info(f"[{request_id}] Checking auth for path: '{path}'")
            
            # Get tokens directly from cookies
            id_token = request.cookies.get("id_token")
            access_token = request.cookies.get("access_token")
            refresh_token_str = request.cookies.get("refresh_token")
                
            logger.info(f"[{request_id}] Cookie tokens - Access: {'Present' if access_token else 'Missing'}, ID: {'Present' if id_token else 'Missing'}, Refresh: {'Present' if refresh_token_str else 'Missing'}")
        except Exception as e:
            # If there's any issue with the cookies, redirect to login page
            logger.error(f"[{request_id}] Cookie error: {str(e)}")
            return RedirectResponse(url="/auth/login")
        
        if not id_token:
            # Redirect to login page
            logger.info(f"[{request_id}] No ID token found in cookies for path '{path}', redirecting to login")
            return RedirectResponse(url="/auth/login")
            
        # Verify token
        try:
            logger.info(f"[{request_id}] Verifying ID token for path '{path}'")
            user = verify_token(id_token)
            logger.info(f"[{request_id}] Token verified successfully for user: {user.get('email')}")
            # Add user to request state
            request.state.user = user
            
            # Special handling for /app path - ensure it's always protected
            if path == "/app":
                logger.info(f"[{request_id}] Authenticated access to app page: '{path}'")
                
            return await call_next(request)
        except Exception as e:
            # Token is invalid, try to refresh
            logger.error(f"[{request_id}] Token verification failed for path '{path}': {str(e)}")
            if refresh_token_str:
                try:
                    # Refresh the token
                    logger.info(f"[{request_id}] Attempting to refresh token for path '{path}'")
                    auth_result = refresh_token(refresh_token_str)
                    logger.info(f"[{request_id}] Token refreshed successfully for path '{path}'")
                    
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
                    
                    logger.info(f"[{request_id}] Updated tokens in cookies for path '{path}'")
                    
                    return response
                except Exception as refresh_error:
                    # Refresh failed, redirect to login
                    logger.error(f"[{request_id}] Token refresh failed for path '{path}': {str(refresh_error)}")
                    response = RedirectResponse(url="/auth/login")
                    response.delete_cookie("access_token")
                    response.delete_cookie("id_token")
                    response.delete_cookie("refresh_token")
                    return response
            else:
                # No refresh token, redirect to login
                logger.info(f"[{request_id}] No refresh token available for path '{path}', redirecting to login")
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
