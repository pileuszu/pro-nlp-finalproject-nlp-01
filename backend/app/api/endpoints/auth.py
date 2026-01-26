from fastapi import APIRouter

router = APIRouter()

@router.get("/kakao/callback")
async def kakao_callback(code: str):
    return {"message": "Kakao login placeholder", "code": code}

@router.get("/me")
async def get_me():
    return {"id": 1, "email": "user@pro-nlp.com", "name": "Tester"}
