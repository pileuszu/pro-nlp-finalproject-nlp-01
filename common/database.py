import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from common.config import settings

# Setup basic logging
# logging.basicConfig(level=logging.INFO) # Removing to avoid interfering with app logger
logger = logging.getLogger(__name__)

# 1. Base URL Parsing
raw_url = settings.DATABASE_URL
url = make_url(raw_url)

# Handle legacy 'postgres' driver name
if url.drivername == "postgres":
    url = url.set(drivername="postgresql")

# --- Private Engine Singletons ---
_engine = None
_async_engine = None
_SessionLocal = None
_AsyncSessionLocal = None

def get_sync_engine():
    global _engine
    if _engine is None:
        # Supabase Pooler (6543) needs sslmode=require
        sync_url = url
        if "supabase.com" in (sync_url.host or "") or "supabase.co" in (sync_url.host or ""):
            if sync_url.port == 6543:
                sync_url = sync_url.update_query_dict({"sslmode": "require"})

        logger.info(f"Sync engine target: {sync_url.host}:{sync_url.port}")
        _engine = create_engine(sync_url, poolclass=NullPool)
    return _engine

def get_async_engine():
    global _async_engine
    if _async_engine is None:
        # Use postgresql+asyncpg driver
        async_url = url.set(drivername="postgresql+asyncpg")

        # asyncpg does not use 'sslmode' query param, but 'ssl' in connect_args or query.
        # We'll strip sslmode from query and use connect_args for SSL.
        query = dict(async_url.query)
        query.pop("sslmode", None)
        async_url = async_url.set(query=query)

        logger.info(f"Async engine target: {async_url.host}:{async_url.port}")

        async_connect_args = {"statement_cache_size": 0}
        if "supabase.com" in (async_url.host or "") or "supabase.co" in (async_url.host or ""):
            async_connect_args["ssl"] = "require"

        _async_engine = create_async_engine(
            async_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            connect_args=async_connect_args
        )
    return _async_engine

# --- Exported Objects (Lazy access via __getattr__) ---

Base = declarative_base()

def get_db():
    # Local import-like access to trigger __getattr__ or just call singletons
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db

def __getattr__(name):
    global _SessionLocal, _AsyncSessionLocal
    if name == "engine":
        return get_sync_engine()
    if name == "async_engine":
        return get_async_engine()
    if name == "SessionLocal":
        if _SessionLocal is None:
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_sync_engine())
        return _SessionLocal
    if name == "AsyncSessionLocal":
        if _AsyncSessionLocal is None:
            _AsyncSessionLocal = async_sessionmaker(get_async_engine(), expire_on_commit=False)
        return _AsyncSessionLocal
    raise AttributeError(f"module {__name__} has no attribute {name}")
