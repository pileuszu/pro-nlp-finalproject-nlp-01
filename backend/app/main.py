from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, recruits, portfolios, cover_letters, health

app = FastAPI(
    title="Pro-NLP AI Recruitment Platform API",
    description="AI 기반 채용 플랫폼의 프론트엔드-백엔드 협업을 위한 표준 API 규격서입니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Pro-NLP AI Recruitment Platform API", "docs": "/docs"}

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["System"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(recruits.router, prefix="/api/recruits", tags=["Recruitments"])
app.include_router(portfolios.router, prefix="/api/portfolios", tags=["Portfolios"])
app.include_router(cover_letters.router, prefix="/api/cover-letters", tags=["Cover Letters"])

