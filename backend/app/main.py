import logging
import sys
import threading
import shutil
import time
from pathlib import Path
from contextlib import asynccontextmanager

# --- 1. Immediate STDOUT Debugging ---
print("STDOUT: main.py loading started", flush=True)
_start_time = time.time()

try:
    from fastapi import FastAPI, Request, status
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from common.config import settings
    from app.core.exceptions import AppBaseException
    print(f"STDOUT: Core libraries imported ({time.time() - _start_time:.2f}s)", flush=True)
except Exception as e:
    print(f"STDOUT: ERROR during early imports: {e}", flush=True)
    raise

# --- 2. Logging Setup (Delayed slightly to ensure core imports work) ---
from app.core.logging_utils import setup_structured_logging
setup_structured_logging()
logger = logging.getLogger("main")
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# --- 3. Background Tasks ---

def run_db_initialization():
    print("STDOUT: Background DB init starting", flush=True)
    try:
        from common.db_init import init_db
        init_db()
        print("STDOUT: Background DB init complete", flush=True)
    except Exception as e:
        print(f"STDOUT: Background DB init ERROR: {e}", flush=True)
        logger.error(f"Background: Database initialization failed: {e}")

def run_startup_cleanup():
    print("STDOUT: Background cleanup starting", flush=True)
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
        print("STDOUT: Background cleanup complete", flush=True)
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

# --- 4. FastAPI App (PRE-ROUTER) ---

print("STDOUT: Defining FastAPI app object", flush=True)
app = FastAPI(
    title="Pro-NLP AI Recruitment Platform API",
    description="Pro-NLP Backend",
    version="1.1.0",
    lifespan=lifespan
)

# Early Health Route (No dependencies)
@app.get("/api/ping")
async def ping():
    return {"status": "pong", "timestamp": time.time()}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Pro-NLP Backend is ready", "docs": "/docs"}

# CORS
origins = ["*"] # Simplified for troubleshooting, can restore specific ones later
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(AppBaseException)
async def app_base_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "detail": exc.message})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"success": False, "detail": "Validation Error", "errors": exc.errors()})

# --- 5. Routing (THE DANGEROUS PART) ---

print("STDOUT: Starting router inclusion", flush=True)
try:
    from app.api.endpoints import auth, recruits, portfolios, cover_letters, health, notifications, integrations, admin
    
    app.include_router(health.router, prefix="/api/health", tags=["System"])
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
    app.include_router(recruits.router, prefix="/api/recruits", tags=["Recruitments"])
    app.include_router(portfolios.router, prefix="/api/portfolios", tags=["Portfolios"])
    app.include_router(cover_letters.router, prefix="/api/cover-letters", tags=["Cover Letters"])
    app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
    app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
    
    print(f"STDOUT: Router inclusion complete ({time.time() - _start_time:.2f}s total)", flush=True)
except Exception as e:
    print(f"STDOUT: ERROR during router inclusion: {e}", flush=True)
    # Don't raise here, let the app start with partial routes if possible for debugging, 
    # but actually it's better to raise so we know it's broken.
    raise

print("STDOUT: FastAPI initialization COMPLETE. Binding to port now.", flush=True)

