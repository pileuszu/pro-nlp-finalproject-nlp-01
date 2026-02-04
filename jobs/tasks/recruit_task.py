import os
import logging
import traceback
from sqlalchemy import select
from common.database import AsyncSessionLocal
from common.models import Portfolio, Recommendation, Recruitment, User
from jobs.services.recruit_service import (
    precompute_recommendations_for_portfolio, 
    global_rerank_recommendations, 
    bulk_precompute_recommendations
)
from jobs.core.recruit.crawler import RecruitmentCrawler
from jobs.core.recruit.indexer import RecruitIndexer
from datetime import datetime

logger = logging.getLogger("recruit_task")

async def process_recruitments(user_id: int = None):
    """
    Heavy task: 
    1. Update recommendations for user's latest portfolio.
    2. Global reranking.
    3. (Optional) Run scraper.
    """
    if user_id:
        async with AsyncSessionLocal() as db:
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
        
        # 1. Scraper logic (Manages its own sessions to prevent timeout)
        await run_scraper() 
        
        # 2. Bulk recommendations (Create a fresh session)
        async with AsyncSessionLocal() as db:
             await bulk_precompute_recommendations(db)

# Scraper logic with disconnected session management
async def run_scraper():
    """
    Runs the RecruitmentCrawler and saves results to the database.
    Process: Check Existing -> Crawl (No DB) -> Save New (New Session)
    """
    logger.info("Starting recruitment scraper process...")
    
    existing_links = set()
    
    # Phase 1: Fetch existing links (Short session)
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(Recruitment.link)
            res = await db.execute(stmt)
            existing_rows = res.all()
            existing_links = {row.link for row in existing_rows if row.link}
            logger.info(f"Loaded {len(existing_links)} existing recruitment links to skip.")
    except Exception as e:
        logger.error(f"Failed to fetch existing recruitments: {e}")
        return

    # Combined Phase 2 & 3: Stream Crawl -> Refine -> Embed -> Save (Incremental)
    try:
        # Read pages and limit from environment
        target_pages = int(os.getenv("JOB_EXTRA_PAGES", "3"))
        crawl_limit = os.getenv("JOB_EXTRA_LIMIT")
        crawl_limit = int(crawl_limit) if crawl_limit else None
        
        logger.info(f"Starting crawler (incremental): target_pages={target_pages}, limit={crawl_limit}")
        crawler = RecruitmentCrawler(target_pages=target_pages)
        indexer = RecruitIndexer()
        
        # Process each item immediately as it is parsed
        processed_count = 0
        async with AsyncSessionLocal() as db:
            async for item in crawler.crawl_and_parse_gen(exclude_links=existing_links, limit=crawl_limit):
                try:
                    # Indexer handles embedding and individual commit
                    await indexer.add_recruitments(db, [item])
                    processed_count += 1
                    if processed_count % 5 == 0:
                        logger.info(f"Progress: Processed {processed_count} items...")
                except Exception as item_e:
                    logger.error(f"Failed to index individual item: {item_e}")
                    continue

        logger.info(f"Incremental sync complete. Total items added/updated: {processed_count}")
    except Exception as e:
        logger.error(f"Incremental crawler task failed: {e}")
        logger.error(traceback.format_exc())
