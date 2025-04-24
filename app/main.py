import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.database.init_db import init_db

# Create FastAPI app
app = FastAPI(
    title="Basketball PDF Analysis Pipeline",
    description="A web application for analyzing basketball PDFs and generating game predictions",
    version="1.0.0"
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """
    Initialize the database when the application starts
    """
    init_db()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Create temp directories if they don't exist
os.makedirs("app/temp/uploads", exist_ok=True)
os.makedirs("app/temp/reports", exist_ok=True)

# Import routers after app is created to avoid circular imports
from app.routers import upload

# Include routers
app.include_router(upload.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint that renders the main page with the file upload form
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/analyses", response_class=HTMLResponse)
async def analyses_page(request: Request):
    """
    Redirect to the analyses API endpoint
    """
    return RedirectResponse(url="/api/analyses")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
