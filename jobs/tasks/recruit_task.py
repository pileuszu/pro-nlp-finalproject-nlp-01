import logging
import traceback
from sqlalchemy import select
from common.database import AsyncSessionLocal
from common.models import Portfolio, Recommendation, Recruitment, User
from jobs.services.recruit_service import precompute_recommendations_for_portfolio, global_rerank_recommendations

logger = logging.getLogger("recruit_task")

async def process_recruitments(user_id: int = None):
    """
    Heavy task: 
    1. Update recommendations for user's latest portfolio.
    2. Global reranking.
    3. (Optional) Run scraper.
    """
    async with AsyncSessionLocal() as db:
        if user_id:
            try:
                # Find latest portfolio
                stmt = select(Portfolio).where(Portfolio.user_id == user_id).order_by(Portfolio.created_at.desc()).limit(1)
                result = await db.execute(stmt)
                portfolio = result.scalar_one_or_none()
                
                if portfolio:
                    logger.info(f"Updating recommendations for User {user_id}, Portfolio {portfolio.id}")
                    await precompute_recommendations_for_portfolio(db, portfolio.id)
                    
                    logger.info(f"Running Global Rerank for User {user_id}")
                    await global_rerank_recommendations(db, user_id)
                else:
                    logger.info(f"No portfolio found for User {user_id}")
            except Exception as e:
                logger.error(f"Recommendation update failed for User {user_id}: {e}")
                logger.error(traceback.format_exc())
        else:
            # Run periodic processing for all users or run scraper
            logger.info("Running general recruitment update (Scraper + Bulk Recommendations)")
            # 1. Scraper logic (from recruitment_info_gathering.py)
            # await run_scraper(db) 
            
            # 2. Bulk recommendations
            from jobs.services.recruit_service import bulk_precompute_recommendations
            await bulk_precompute_recommendations(db)

# Placeholder for scraper logic if integrated
async def run_scraper(db):
    logger.info("Running recruitment scraper...")
    # This would call the logic from llm-pipeline/recruit/src/recruitment_info_gathering.py
    # but adapted for direct DB insertion.
    pass
