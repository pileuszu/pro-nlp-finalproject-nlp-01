import logging
from common.database import AsyncSessionLocal
from jobs.services.ai_cover_letter_service import ai_cover_letter_service

logger = logging.getLogger("cover_letter_task")

async def process_cover_letter(cl_id: int):
    """
    Heavy task: Cover Letter Generation.
    Delegates entire logic to AICoverLetterService.
    """
    logger.info(f"Starting Cover Letter Generation for ID: {cl_id}")
    
    async with AsyncSessionLocal() as db:
        try:
            await ai_cover_letter_service.process_cover_letter_generation(db, cl_id)
        except Exception as e:
            logger.error(f"Task Failed: {e}")
            # Service handles internal status updates to FAILED, 
            # but we catch here to ensure job runner knows it failed for logging.
            raise

