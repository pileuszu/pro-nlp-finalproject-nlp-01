import logging
import sys
import threading
import shutil
import time
import os
from pathlib import Path
from contextlib import asynccontextmanager

# --- 1. Immediate STDOUT Debugging ---
print(f"STDOUT: main.py loading started at {time.time()}", flush=True)
print(f"STDOUT: PORT={os.environ.get('PORT', '8080')}", flush=True)

_start_time = time.time()

try:
    from fastapi import FastAPI, Request, status
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from common.config import settings
    from app.core.exceptions import AppBaseException
    print(f"STDOUT: Core libraries imported in {time.time() - _start_time:.2f}s", flush=True)
except Exception as e:
    print(f"STDOUT: CRITICAL ERROR during early imports: {e}", flush=True)
    sys.exit(1)

# --- 2. Logging Setup ---
from app.core.logging_utils import setup_structured_logging
setup_structured_logging()
logger = logging.getLogger("main")
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# --- 3. Background Tasks ---

def run_db_initialization():
    print("STDOUT: Background DB init starting...", flush=True)
    try:
        from common.db_init import init_db
        init_db()
        print("STDOUT: Background DB init complete.", flush=True)
    except Exception as e:
        print(f"STDOUT: Background DB init ERROR: {e}", flush=True)
        logger.error(f"Background: Database initialization failed: {e}")

def run_startup_cleanup():
    print("STDOUT: Background cleanup starting...", flush=True)
    try:
        upload_dir = Path("/tmp/uploads")
        if upload_dir.exists():
            for item in upload_dir.iterdir():
                try:
                    if item.is_file(): item.unlink()
                    elif item.is_dir(): shutil.rmtree(item)
                except Exception: pass
        else:
            upload_dir.mkdir(parents=True, exist_ok=True)
        print("STDOUT: Background cleanup complete.", flush=True)
    except Exception as e:
        print(f"STDOUT: Background cleanup ERROR: {e}", flush=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fire off background tasks
    logger.info("Lifespan: Starting background tasks...")
    threading.Thread(target=run_db_initialization, daemon=True).start()
    threading.Thread(target=run_startup_cleanup, daemon=True).start()
    yield
    logger.info("Lifespan: Shutting down...")

# --- 4. FastAPI App Definition ---

print("STDOUT: Initializing FastAPI app object...", flush=True)
app = FastAPI(
    title="Pro-NLP AI Recruitment Platform API",
    description="Pro-NLP Backend",
    version="1.1.1",
    lifespan=lifespan
)

# CORS - Using * for troubleshooting to avoid any issues during startup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ping")
async def ping():
    return {"status": "pong", "timestamp": time.time()}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Pro-NLP Backend", "docs": "/docs"}

# Exception Handlers
@app.exception_handler(AppBaseException)
async def app_base_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "detail": exc.message})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"success": False, "detail": "Validation Error", "errors": exc.errors()})

# --- 5. Lazy Router Inclusion ---

def include_routers():
    """Import and include routers with detailed tracing."""
    print("STDOUT: Starting router inclusion process...", flush=True)
    _routers_start = time.time()
    
    try:
        print("DEBUG: Importing auth...", flush=True)
        from app.api.endpoints import auth
        app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
        
        print("DEBUG: Importing recruits...", flush=True)
        from app.api.endpoints import recruits
        app.include_router(recruits.router, prefix="/api/recruits", tags=["Recruitments"])
        
        print("DEBUG: Importing portfolios...", flush=True)
        from app.api.endpoints import portfolios
        app.include_router(portfolios.router, prefix="/api/portfolios", tags=["Portfolios"])
        
        print("DEBUG: Importing cover_letters...", flush=True)
        from app.api.endpoints import cover_letters
        app.include_router(cover_letters.router, prefix="/api/cover-letters", tags=["Cover Letters"])
        
        print("DEBUG: Importing system endpoints...", flush=True)
        from app.api.endpoints import health, notifications, integrations, admin
        app.include_router(health.router, prefix="/api/health", tags=["System"])
        app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
        app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
        app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
        
        print(f"STDOUT: All routers included in {time.time() - _routers_start:.2f}s", flush=True)
    except Exception as e:
        print(f"STDOUT: ERROR during router inclusion: {e}", flush=True)
        # Continue starting even if some routers fail, so we can at least ping the app
        # raise e

# Execute router inclusion immediately (still before port bind, but with tracing)
include_routers()

print(f"STDOUT: FastAPI initialization COMPLETE in {time.time() - _start_time:.2f}s total. Ready for port binding.", flush=True)

