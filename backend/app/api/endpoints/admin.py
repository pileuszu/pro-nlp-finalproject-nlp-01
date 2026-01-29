from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from typing import List
import subprocess
import sys
import os
from pathlib import Path
from app.db.database import get_async_db

router = APIRouter()

# Define script path (adjust based on deployment structure)
# Assuming llm-pipeline is a sibling of backend or deployed together
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SCRAPER_SCRIPT = BASE_DIR / "llm-pipeline" / "recruit" / "src" / "recruitment_info_gathering.py"
OUTPUT_JSON = BASE_DIR / "llm-pipeline" / "recruit" / "data" / "recruit_data" / "final_recruitment_all_items.json"

async def run_crawler_script(db_session_factory):
    """Background task to run the crawler script and index results."""
    import json
    import logging
    import asyncio
    from app.core.recruit.indexer import RecruitIndexer

    logger = logging.getLogger("crawler")
    logging.basicConfig(level=logging.INFO)

    try:
        # 1. Run Crawler
        if not SCRAPER_SCRIPT.exists():
            logger.error(f"Error: Scraper script not found at {SCRAPER_SCRIPT}")
            return

        logger.info(f"Triggering crawler: {SCRAPER_SCRIPT}")
        
        # Use asyncio subprocess to avoid blocking the event loop
        # Pass current environment variables to the subprocess
        env = os.environ.copy()
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(SCRAPER_SCRIPT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(SCRAPER_SCRIPT.parent),
            env=env
        )
        
        stdout, stderr = await process.communicate()
        stdout_text = stdout.decode().strip()
        stderr_text = stderr.decode().strip()
        
        if process.returncode != 0:
            logger.error(f"Crawler Failed with code {process.returncode}:\nSTDERR: {stderr_text}\nSTDOUT: {stdout_text}")
            return
        else:
            logger.info(f"Crawler Success:\n{stdout_text}")

        # 2. Index Data
        if not OUTPUT_JSON.exists():
             logger.error(f"Error: Output JSON not found at {OUTPUT_JSON}")
             return

        logger.info(f"Indexing data from {OUTPUT_JSON}...")
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Create a new session for this background operation
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
    return {"message": "Crawling started in background", "script_path": str(SCRAPER_SCRIPT)}

@router.delete("/clear", status_code=200)
async def clear_database(
    secret: str,
    db = Depends(get_async_db)  # Use dependency for session
):
    """
    Clear all recruitment and recommendation data.
    """
    # Security check
    ADMIN_SECRET = os.getenv("ADMIN_SECRET", "nlp-final-admin-secret")
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    try:
        from sqlalchemy import text
        # Order matters due to foreign keys (delete recommendations first)
        await db.execute(text("DELETE FROM recommendations"))
        await db.execute(text("DELETE FROM recruitments"))
        
        # Clear vector embeddings (portfolio and recruitment)
        await db.execute(text("DELETE FROM langchain_pg_embedding"))
        await db.execute(text("DELETE FROM langchain_pg_collection"))
        
        await db.commit()
        return {"message": "Recruitments, Recommendations, and Vector Embeddings cleared successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear DB: {str(e)}")
