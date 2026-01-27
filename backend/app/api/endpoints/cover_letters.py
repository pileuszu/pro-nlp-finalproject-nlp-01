from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import schemas
from app.services import cover_letter_service
from app.api import deps
from app.models import models

router = APIRouter()

@router.get("", response_model=schemas.CoverLetterListResponse)
async def list_cover_letters(
    recruitId: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    items = cover_letter_service.get_cover_letters(db, user_id=current_user.id, recruitment_id=recruitId)
    return {"items": items}

@router.post("/", response_model=schemas.CoverLetter, status_code=201)
async def create_cover_letter(
    cl: schemas.CoverLetterCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Convert Request schema to internal Create schema (adding user_id)
    cl_data = cl.model_dump()
    # Handle potential field mismatch if service expects strict schema
    # We create the internal schema object
    internal_cl = schemas.CoverLetterCreate(**cl_data, user_id=current_user.id)
    return cover_letter_service.create_cover_letter(db, internal_cl)

@router.get("/{cl_id}", response_model=schemas.CoverLetter)
async def get_cover_letter(
    cl_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    db_cl = cover_letter_service.get_cover_letter(db, cl_id, current_user.id)
    if not db_cl:
        raise HTTPException(status_code=404, detail="Cover letter not found or unauthorized")
    return db_cl

@router.put("/{cl_id}", response_model=schemas.CoverLetter)
async def update_cover_letter(
    cl_id: int, 
    content: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    db_cl = cover_letter_service.update_cover_letter(db, cl_id, current_user.id, content)
    if not db_cl:
        raise HTTPException(status_code=404, detail="Cover letter not found or unauthorized")
    return db_cl

@router.delete("/{cl_id}")
async def delete_cover_letter(
    cl_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    success = cover_letter_service.delete_cover_letter(db, cl_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Cover letter not found or unauthorized")
    return {"success": True, "message": "Cover letter deleted"}

@router.post("/generate", response_model=dict)
async def generate_cover_letter(req: schemas.CoverLetterGenerateRequest):
    """Mocks AI generation of a cover letter."""
    result = cover_letter_service.mock_generate_cover_letter(req)
    return {"result": result}
