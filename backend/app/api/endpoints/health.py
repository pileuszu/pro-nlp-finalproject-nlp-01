from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from common.database import get_db, get_async_db

router = APIRouter()

@router.get("")
@router.get("")
async def health_check(
    async_db: AsyncSession = Depends(get_async_db)
):
    """
    Check if the API and Async Database connection is working.
    """
    results = {
        "status": "healthy",
        "async_db": "unknown",
        "message": "API is up"
    }

    try:
        await async_db.execute(text("SELECT 1"))
        results["async_db"] = "connected"
    except Exception as e:
        results["async_db"] = f"failed: {str(e)}"
        results["status"] = "unhealthy"

    return results
