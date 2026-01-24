from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import schemas
from app.services import cover_letter_service

router = APIRouter()

@router.get("/", response_model=dict)
async def list_cover_letters(db: Session = Depends(get_db)):
    user_id = 1
    items = cover_letter_service.get_cover_letters(db, user_id=user_id)
    return {"items": items}

@router.post("/", response_model=schemas.CoverLetter, status_code=201)
async def create_cover_letter(cl: schemas.CoverLetterCreate, db: Session = Depends(get_db)):
    return cover_letter_service.create_cover_letter(db, cl)

@router.put("/{cl_id}", response_model=schemas.CoverLetter)
async def update_cover_letter(cl_id: int, content: str, db: Session = Depends(get_db)):
    user_id = 1
    db_cl = cover_letter_service.update_cover_letter(db, cl_id, user_id, content)
    if not db_cl:
        raise HTTPException(status_code=404, detail="Cover letter not found or unauthorized")
    return db_cl

@router.delete("/{cl_id}")
async def delete_cover_letter(cl_id: int, db: Session = Depends(get_db)):
    user_id = 1
    success = cover_letter_service.delete_cover_letter(db, cl_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cover letter not found or unauthorized")
    return {"success": True, "message": "Cover letter deleted"}

@router.post("/generate", response_model=dict)
async def generate_cover_letter(req: schemas.CoverLetterGenerateRequest):
    """Mocks AI generation of a cover letter."""
    result = cover_letter_service.mock_generate_cover_letter(req)
    return {"result": result}
