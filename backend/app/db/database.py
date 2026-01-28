import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

from sqlalchemy.pool import NullPool

raw_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pro_nlp_db")

# Handle legacy 'postgres://' prefix often provided by platforms
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = raw_url
logger.info(f"Initializing database engines... (Sync: {DATABASE_URL.split('@')[-1]})")

# Sync Engine
engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Engine
# Ensure we don't double-replace if it already has a driver specified
if "postgresql+asyncpg://" not in DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

logger.info(f"Async engine target: {ASYNC_DATABASE_URL.split('@')[-1]}")
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=NullPool,
    connect_args={"statement_cache_size": 0}
)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db
