import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import models
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Environment variables
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "https://pro-nlp-finalproject-nlp-01.onrender.com/api/auth/kakao/callback")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/kakao/callback")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    # 1. Exchange code for token
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_REST_API_KEY,
                "client_secret": KAKAO_CLIENT_SECRET,
                "redirect_uri": KAKAO_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to get token: {token_res.text}")
        
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        # 2. Get user info
        user_res = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        kakao_user = user_res.json()
        kakao_account = kakao_user.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        
        email = kakao_account.get("email")
        if not email:
            # Fallback for kakao account without email (using internal ID)
            email = f"{kakao_user['id']}@kakao.com"
            
        name = profile.get("nickname", "Kakao User")
        profile_image = profile.get("profile_image_url")

        # 3. DB Check & Create
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(
                email=email,
                name=name,
                profile_image=profile_image
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 4. Create Local Token
        local_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        
        return {
            "access_token": local_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "profile_image": user.profile_image
            }
        }

@router.get("/me")
async def get_me():
    # Placeholder - in real app, use a dependency to verify token
    return {"id": 1, "email": "user@pro-nlp.com", "name": "Tester"}
