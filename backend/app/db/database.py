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

try:
    load_dotenv()
except Exception:
    pass

from sqlalchemy.pool import NullPool

raw_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pro_nlp_db")

# Handle legacy 'postgres://' prefix
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

# Enforce sslmode=require for Supabase Pooler (port 6543) if not present
if "supabase.com:6543" in raw_url and "sslmode=" not in raw_url:
    separator = "&" if "?" in raw_url else "?"
    raw_url += f"{separator}sslmode=require"

DATABASE_URL = raw_url
# Use a safer logging that won't crash if URL is weird
try:
    url_tag = DATABASE_URL.split('@')[-1].split('?')[0]
except Exception:
    url_tag = "unknown"
logger.info(f"Initializing database engines... (Target: {url_tag})")

# Sync Engine
engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Engine setup
# asyncpg (used by asyncpg driver) does not support 'sslmode' in the query string.
# We must strip it for the async URL but keep it for the sync URL.
if "postgresql+asyncpg://" not in DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Clean ASYNC_DATABASE_URL of 'sslmode'
if "?" in ASYNC_DATABASE_URL:
    base_url, query_str = ASYNC_DATABASE_URL.split("?", 1)
    # Filter out sslmode
    params = [p for p in query_str.split("&") if not p.startswith("sslmode=")]
    ASYNC_DATABASE_URL = base_url + ("?" + "&".join(params) if params else "")

try:
    async_tag = ASYNC_DATABASE_URL.split('@')[-1].split('?')[0]
except Exception:
    async_tag = "unknown"
logger.info(f"Async engine target: {async_tag}")

# asyncpg handles SSL differently (via connect_args or 'ssl' param)
async_connect_args = {"statement_cache_size": 0}
# Supabase requires SSL for the pooler (6543) and usually for direct (5432) on cloud
if "supabase.co" in ASYNC_DATABASE_URL or "supabase.com" in ASYNC_DATABASE_URL:
    async_connect_args["ssl"] = "require"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=NullPool,
    connect_args=async_connect_args
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
