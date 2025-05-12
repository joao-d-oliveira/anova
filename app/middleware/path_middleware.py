from fastapi import Request
from starlette.middleware.base import BaseHTleware
import os

class PathMiddleware(BaseHTleware):
    """
    Middleware to handle base path prefixes in different environments.
    This ensures static files and routes work both locally and in ECS.
    """
    async def dispatch(self, request: Request, call_next):
        # Get the root_path from environment or use default empty string
        root_path = os.getenv("ROOT_PATH", "")
        
        # Store the root_path in request state for use in templates
        request.state.root_path = root_path
        
        # Continue processing the request
        response = await call_next(request)
        return response