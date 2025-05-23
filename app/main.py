import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers import auth, report, upload
from app.config import Config
from app.database.init_db import init_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration
config = Config()

# Log startup information
logger.info(f"Starting application in directory: {os.getcwd()}")
logger.info(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
logger.info(f"ROOT_PATH: {os.getenv('ROOT_PATH', 'Not set')}")
logger.info(f"Environment: {config.environment}")
logger.info(f"Database: {config.db_host}:{config.db_port}/{config.db_name}")

# Create FastAPI app
app = FastAPI(
    title="Basketball PDF Analysis Pipeline",
    description="A web application for analyzing basketball PDFs and generating game predictions",
    version="1.0.0"
)

# Add middlewares
# app.add_middleware(AuthMiddleware)
# app.add_middleware(PathMiddleware)

# Define important directories
root = Path(__file__).parent
static_dir = root / "frontend" / "dist"

# Initialize database
@app.on_event("startup")
async def startup_event():
    """
    Initialize the database when the application starts
    """
    logger.info("Initializing database...")
    init_db(config)
    logger.info("Database initialization complete")
    
    logger.info(f"Base directory: {root}")
    logger.info(f"Static directory: {static_dir}")
    logger.info(f"Static directory exists: {static_dir.exists()}")
    
# Mount static files with absolute path

logger.info(f"Mounting static files from: {static_dir}")

app.mount( "/static", StaticFiles(directory=static_dir), name="static")

# Add root_path to all templates
# @app.middleware("http")
# async def add_root_path_to_templates(request: Request, call_next):
#     # Get root_path from environment or use empty string
#     root_path = os.getenv("ROOT_PATH", "")
#     request.state.root_path = root_path
    
#     # Get request ID from auth middleware if available
#     request_id = getattr(request.state, "request_id", "no-id")
#     logger.info(f"[{request_id}] Template middleware processing request for path: {request.url.path}")
    
#     response = await call_next(request)
#     return response

# Create temp directories if they don't exist
root = os.path.dirname(os.path.abspath(__file__))
temp_uploads_dir = os.path.join(root, "temp/uploads")
temp_reports_dir = os.path.join(root, "temp/reports")

logger.info(f"Creating temp directories: {temp_uploads_dir}, {temp_reports_dir}")
os.makedirs(temp_uploads_dir, exist_ok=True)
os.makedirs(temp_reports_dir, exist_ok=True)



# Include routers
app.include_router(upload.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(report.router, prefix="/api")

def get_version_date():
    """
    Read the VERSION_DEPLOYMENT.JSON file and return the last_updated date
    """

    root = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(root, "VERSION_DEPLOYMENT.JSON")
    logger.info(f"Reading version file: {version_file}")
    
    try:
        with open(version_file, "r") as f:
            version_data = json.load(f)
            version_date = version_data.get("last_updated", "Unknown")
            logger.info(f"Version date: {version_date}")
            return version_date
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error reading version file: {str(e)}")
        return "Unknown"


@app.get("/maintenance", response_class=HTMLResponse)
async def maintenance_page(request: Request):
    """
    Display maintenance page when services are unavailable
    """
    # Get request ID from auth middleware if available
    request_id = getattr(request.state, "request_id", "no-id")
    logger.info(f"[{request_id}] Maintenance page requested")
    
    try:
        # todo: replace maintenance page
        return RedirectResponse(url="/")
    except Exception as e:
        logger.error(f"[{request_id}] Error rendering maintenance page: {str(e)}")
        raise


@app.get("/analyses", response_class=HTMLResponse)
async def analyses_page(request: Request):
    """
    Redirect to the analyses API endpoint
    """
    return RedirectResponse(url="/api/analyses")


@app.get("/{path:path}")
async def read_root(path: str):
    # Don't handle API routes here
    if path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    if path.startswith("."):
        return Response(status_code=404)

    full_path = static_dir / path.lstrip("/") / "index.html"
    if full_path.exists():
        return FileResponse(full_path)
    elif (file_path := static_dir / path.lstrip("/")).exists():
        return FileResponse(file_path)
    else:
        return FileResponse(static_dir / "404/index.html", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
