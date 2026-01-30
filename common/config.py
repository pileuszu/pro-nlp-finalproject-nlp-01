import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Config
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENV: str = os.getenv("ENV", "development")
    
    # GCP Config
    GCP_PROJECT_ID: Optional[str] = os.getenv("GCP_PROJECT_ID")
    GCP_REGION: str = os.getenv("GCP_REGION", "asia-northeast3")
    CLOUD_RUN_JOB_NAME: str = os.getenv("CLOUD_RUN_JOB_NAME", "pro-nlp-jobs")

    # AI / LLM Keys
    NCP_CLOVASTUDIO_API_KEY: str = os.getenv("NCP_CLOVASTUDIO_API_KEY", "")
    NCP_CLOVASTUDIO_BASE_URL: str = os.getenv("NCP_CLOVASTUDIO_BASE_URL", "https://clovastudio.stream.ntruss.com")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Kakao
    KAKAO_REST_API_KEY: str = os.getenv("KAKAO_REST_API_KEY", "")
    KAKAO_CLIENT_SECRET: str = os.getenv("KAKAO_CLIENT_SECRET", "")
    KAKAO_REDIRECT_URI: str = os.getenv("KAKAO_REDIRECT_URI", "")

    # Job Config
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")

    # DB Config
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pro_nlp_db")

    # Admin Config
    ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "nlp-final-admin-secret")

    class Config:
        case_sensitive = True

settings = Settings()
