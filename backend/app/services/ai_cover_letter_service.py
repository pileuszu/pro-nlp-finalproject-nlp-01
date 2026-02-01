import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common import models
from common import schemas
from app.services.job_service import job_service

logger = logging.getLogger(__name__)

class AICoverLetterService:
    async def generate_cover_letter(
        self, 
        db: AsyncSession, 
        user_id: int, 
        generate_req: schemas.CoverLetterGenerateRequest
    ) -> models.CoverLetter:
        """
        Creates placeholders for multiple questions and triggers the AI generation job.
        """
        # 1. Fetch Recruitment
        stmt = select(models.Recruitment).where(models.Recruitment.id == generate_req.recruit_id)
        result = await db.execute(stmt)
        recruitment = result.scalar_one_or_none()
        
        if not recruitment:
            raise ValueError("Recruitment not found")

        # 2. Create Header Record
        cover_letter = models.CoverLetter(
            user_id=user_id,
            recruitment_id=recruitment.id,
            title=f"{recruitment.company} - {recruitment.title} 자소서 (생성 중)",
            content="일괄 작성 중입니다...",
            processing_status=models.ProcessingStatus.PENDING,
            gap_analysis={}
        )
        try:
            db.add(cover_letter)
            await db.flush() # Get ID

            # 3. Create Placeholder Items for each question
            for q_text in generate_req.questions:
                item = models.CoverLetterItem(
                    cover_letter_id=cover_letter.id,
                    question=q_text,
                    content="AI가 내용을 구성하고 있습니다...",
                    category="general"
                )
                db.add(item)
            
            await db.commit()
            await db.refresh(cover_letter)
        except Exception as e:
            logger.error(f"Failed to create cover letter placeholders: {e}")
            await db.rollback()
            raise e
        
        # 4. Trigger Job (Bulk)
        # We don't need to pass 'question' in env vars anymore as the Job will fetch from DB items
        success = job_service.trigger_job(
            task="cover_letter_generation", 
            target_id=cover_letter.id,
            tone=generate_req.tone,
            portfolio_ids=generate_req.portfolio_ids
        )
        
        if not success:
            logger.warning(f"Job trigger failed for cover letter {cover_letter.id}. Marking as FAILED.")
            try:
                cover_letter.processing_status = models.ProcessingStatus.FAILED
                await db.commit()
            except Exception as e_inner:
                logger.error(f"Failed to mark cover letter as FAILED: {e_inner}")
                await db.rollback()
        
        return cover_letter

ai_service = AICoverLetterService()
