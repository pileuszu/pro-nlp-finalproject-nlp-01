from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

def get_cover_letters(db: Session, user_id: int):
    return db.query(models.CoverLetter).filter(models.CoverLetter.user_id == user_id).all()

def get_cover_letter(db: Session, cl_id: int, user_id: int):
    return db.query(models.CoverLetter).filter(models.CoverLetter.id == cl_id, models.CoverLetter.user_id == user_id).first()

def create_cover_letter(db: Session, cl: schemas.CoverLetterCreate):
    db_cl = models.CoverLetter(**cl.model_dump())
    db.add(db_cl)
    db.commit()
    db.refresh(db_cl)
    return db_cl

def update_cover_letter(db: Session, cl_id: int, user_id: int, content: str):
    db_cl = get_cover_letter(db, cl_id, user_id)
    if not db_cl:
        return None
    db_cl.content = content
    db.commit()
    db.refresh(db_cl)
    return db_cl

def delete_cover_letter(db: Session, cl_id: int, user_id: int):
    db_cl = get_cover_letter(db, cl_id, user_id)
    if not db_cl:
        return False
    db.delete(db_cl)
    db.commit()
    return True

def mock_generate_cover_letter(req: schemas.CoverLetterGenerateRequest):
    # Mock data for AI generation
    tone_styles = {
        "professional": "As a highly motivated developer...",
        "creative": "Passionate about building the future of AI...",
        "warm": "I have always enjoyed solving problems through code..."
    }
    content = tone_styles.get(req.tone, tone_styles["professional"])
    return f"[MOCK AI GENERATION]\nQuestion: {req.question}\n\n{content}\n\nThis is a placeholder result since the AI pipeline is in another branch."
