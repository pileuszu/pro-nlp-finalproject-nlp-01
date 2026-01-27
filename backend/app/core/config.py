import os

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Kakao
    KAKAO_REST_API_KEY: str = os.getenv("KAKAO_REST_API_KEY", "")
    KAKAO_CLIENT_SECRET: str = os.getenv("KAKAO_CLIENT_SECRET", "")
    KAKAO_REDIRECT_URI: str = os.getenv("KAKAO_REDIRECT_URI", "https://pro-nlp-finalproject-nlp-01.onrender.com/api/auth/kakao/callback")

settings = Settings()
