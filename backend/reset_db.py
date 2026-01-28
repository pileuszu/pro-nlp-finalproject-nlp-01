import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from dotenv import load_dotenv
from app.models.models import Base

# Load env vars
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")
    
# Ensure Async URL
if "postgresql://" in DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

async def reset_database():
    print(f"Connecting to {ASYNC_DATABASE_URL}...")
    engine = create_async_engine(
        ASYNC_DATABASE_URL, 
        echo=True,
        connect_args={"statement_cache_size": 0} # Fix for Supabase Transaction Pooler
    )
    
    async with engine.begin() as conn:
        print("Dropping all tables...")
        
        # Explicitly drop orphaned tables that might not be in Base metadata anymore
        await conn.execute(text("DROP TABLE IF EXISTS portfolio_projects CASCADE"))
        
        await conn.run_sync(Base.metadata.drop_all)
        print("All tables dropped.")
        
        # Also drop the alembic_version table manually if it exists
        try:
             await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
             print("Dropped alembic_version table.")
        except Exception as e:
            print(f"Warning dropping alembic_version: {e}")

    await engine.dispose()
    print("Database reset complete.")

if __name__ == "__main__":
    asyncio.run(reset_database())
