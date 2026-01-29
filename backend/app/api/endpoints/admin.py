from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from typing import List
import os
from app.db.database import get_async_db

router = APIRouter()

async def run_crawler_script(db_session_factory):
    """Background task to run the crawler and index results."""
    import logging
    from app.core.recruit.indexer import RecruitIndexer
    from app.core.recruit.crawler import RecruitmentCrawler

    logger = logging.getLogger("crawler")
    logging.basicConfig(level=logging.INFO)

    try:
        logger.info("Starting recruitment crawler...")
        
        # Run crawler
        crawler = RecruitmentCrawler(target_pages=1)
        data = await crawler.crawl_and_parse()
        
        if not data:
            logger.warning("No data returned from crawler")
            return
        
        logger.info(f"Crawler returned {len(data)} items. Indexing to database...")
        
        # Index data
        async with db_session_factory() as db:
            indexer = RecruitIndexer()
            count = await indexer.add_recruitments(db, data)
            logger.info(f"Successfully indexed {count} items.")

    except Exception as e:
        logger.error(f"Crawler/Indexer Task Exception: {e}", exc_info=True)

@router.post("/crawl", status_code=202)
def trigger_crawling(background_tasks: BackgroundTasks, secret: str):
    """
    Trigger the recruitment crawling process in the background.
    Requires a secret key for basic security.
    """
    ADMIN_SECRET = os.getenv("ADMIN_SECRET", "nlp-final-admin-secret")
    
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
    
    from app.db.database import AsyncSessionLocal
    background_tasks.add_task(run_crawler_script, AsyncSessionLocal)
    return {"message": "Crawling started in background"}

@router.delete("/clear", status_code=200)
async def clear_database(
    secret: str,
    db = Depends(get_async_db)  # Use dependency for session
):
    """
    Clear ALL database tables (users, portfolios, recruitments, cover letters, recommendations).
    WARNING: This will delete everything!
    """
    # Security check
    ADMIN_SECRET = os.getenv("ADMIN_SECRET", "nlp-final-admin-secret")
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    try:
        from sqlalchemy import text
        
        # 1. Get all tables in the public schema except alembic_version
        get_tables_query = text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
              AND tablename <> 'alembic_version'
        """)
        result = await db.execute(get_tables_query)
        tables = [row[0] for row in result.all()]
        
        if not tables:
            return {"message": "No tables found to clear.", "cleared_tables": []}
            
        # 2. Dynamic truncate with CASCADE
        # Quoting table names to handle any special characters
        table_list_str = ", ".join([f'public."{t}"' for t in tables])
        truncate_query = text(f"TRUNCATE TABLE {table_list_str} CASCADE")
        
        await db.execute(truncate_query)
        await db.commit()
        
        return {
            "message": "All public database tables (except alembic_version) cleared successfully.",
            "cleared_count": len(tables),
            "cleared_tables": tables
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear DB: {str(e)}")
