import logging
import os
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common import models
from jobs.core.cover_letter.retriever import PGHybridRetriever
from jobs.core.cover_letter.generator import CoverLetterGenerator

logger = logging.getLogger(__name__)

class AICoverLetterService:
    """
    Orchestrator for Cover Letter Generation Job.
    Delegates retrieval to PGHybridRetriever and generation to CoverLetterGenerator.
    """
    def __init__(self):
        self.generator = CoverLetterGenerator()

    async def process_cover_letter_generation(self, db: AsyncSession, cl_id: int):
        """
        Full pipeline: Fetch data -> Retrieve Context -> Analyze Gap -> Generate Answer -> Save.
        """
        # 1. Fetch Cover Letter
        stmt = select(models.CoverLetter).where(models.CoverLetter.id == cl_id)
        result = await db.execute(stmt)
        cl = result.scalar_one_or_none()
        
        if not cl:
            logger.error(f"Cover Letter {cl_id} not found")
            return

        try:
            # 2. Fetch Recruitment
            recruitment = (await db.execute(select(models.Recruitment).where(models.Recruitment.id == cl.recruitment_id))).scalar_one_or_none()
            if not recruitment:
                raise ValueError("Recruitment not found")

            # 3. Initialize Retriever
            retriever = PGHybridRetriever(db, cl.user_id)
            await retriever.load_documents()

            # Prepare Query for Retrieval
            query_embedding = None
            if recruitment.embedding is not None:
                if isinstance(recruitment.embedding, str):
                    try:
                        query_embedding = json.loads(recruitment.embedding)
                    except: pass
                else:
                    query_embedding = recruitment.embedding

            query_text = f"{recruitment.company} {recruitment.title} {recruitment.required_qualifications or ''}"
            
            # 4. Retrieve Context
            relevant_docs = retriever.search(query_text, query_embedding, top_k=5)
            context_text = "\n\n".join([d.page_content for d in relevant_docs])

            # 5. Gap Analysis
            gap_result = self.generator.analyze_gap(context_text, query_text)
            cl.gap_analysis = gap_result
            await db.commit()

            # 6. Generate Answer
            # Retrieve parameters from Environment (passed by JobService) or DB
            # Ideally these should be in the DB model or passed clearly.
            # Here we follow existing pattern of Env Vars for job params or fallback to title
            question = os.getenv("JOB_EXTRA_QUESTION", cl.title)
            tone = os.getenv("JOB_EXTRA_TONE", "professional")

            logger.info(f"Generating answer for question: {question} with tone: {tone}")

            answer_data = self.generator.generate_answer(
                company_name=recruitment.company,
                job_title=recruitment.title,
                question=question,
                context=context_text,
                gap_analysis=gap_result,
                tone=tone
            )

            # 7. Save Result
            item = models.CoverLetterItem(
                cover_letter_id=cl.id,
                question=question,
                content=answer_data.get("content"),
                key_points=answer_data.get("key_points"),
                suggested_improvements=answer_data.get("suggested_improvements"),
                category="general"
            )
            db.add(item)

            # Update Main Status
            cl.processing_status = "COMPLETED"
            cl.content = answer_data.get("content")
            await db.commit()
            
            logger.info(f"Successfully generated cover letter {cl_id}")

        except Exception as e:
            logger.error(f"Generation Failed for Cover Letter {cl_id}: {e}")
            cl.processing_status = "FAILED"
            await db.commit()
            raise

# Singleton instance
ai_cover_letter_service = AICoverLetterService()

