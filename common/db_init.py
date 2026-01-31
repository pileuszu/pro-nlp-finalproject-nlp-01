import logging
import traceback
from sqlalchemy import text, create_engine
from sqlalchemy.pool import NullPool
from common.database import engine as default_engine, Base
from common import models
from common.config import settings

logger = logging.getLogger(__name__)

def get_ddl_engine():
    """
    Returns a sync engine suitable for DDL operations.
    If the default DATABASE_URL points to Supabase Pooler (6543),
    it attempts to use the Direct Connection port (5432).
    """
    url = settings.DATABASE_URL
    if "supabase.com:6543" in url or "supabase.co:6543" in url:
        logger.info("Supabase Pooler detected. Attempting to use direct port 5432 for DDL operations...")
        url = url.replace(":6543", ":5432")
        # Ensure sslmode=require for direct connection as well
        if "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}sslmode=require"
    
    return create_engine(url, poolclass=NullPool)

def init_db():
    """
    Synchronizes the database schema and ensures Enum types are healthy.
    """
    logger.info("Starting database initialization...")
    
    # Use a specialized engine for DDL to avoid pooler transaction issues
    ddl_engine = get_ddl_engine()
    
    try:
        # 1. Create tables if they don't exist
        logger.info("Syncing tables via SQLAlchemy metadata...")
        Base.metadata.create_all(bind=ddl_engine)
        logger.info("Table sync complete.")

        # 2. Ensure Extensions (vector for recruitment/portfolio embeddings)
        try:
            with ddl_engine.connect() as conn:
                conn = conn.execution_options(isolation_level="AUTOCOMMIT")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("Ensured 'vector' extension exists.")
        except Exception as e:
            logger.warning(f"Could not ensure 'vector' extension (may require superuser or dashboard activation): {e}")

        # 3. Heal Enum: 'processingstatus'
        try:
            with ddl_engine.connect() as conn:
                # Check if the type exists first
                exists = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'processingstatus'")).fetchone()
                
                if exists:
                    logger.info("Healing 'processingstatus' enum values...")
                    # ALTER TYPE cannot run in a transaction
                    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
                    
                    # These are the values defined in common/models.py
                    expected_values = ["PENDING", "PROCESSING", "REVIEW_REQUIRED", "COMPLETED", "FAILED"]
                    
                    for val in expected_values:
                        try:
                            # Using IF NOT EXISTS (PG 9.4+)
                            conn.execute(text(f"ALTER TYPE processingstatus ADD VALUE IF NOT EXISTS '{val}'"))
                            logger.debug(f"Ensured '{val}' exists in processingstatus.")
                        except Exception as inner_e:
                            logger.debug(f"Info: Could not add value '{val}' to enum: {inner_e}")
                else:
                    logger.info("'processingstatus' type not found. It will be created when tables using it are created.")
        except Exception as e:
            logger.warning(f"Enum healing failed (may be due to pooler restrictions): {e}")

        # 4. Heal Columns for existing tables
        try:
            with ddl_engine.connect() as conn:
                # Helper to check and add columns
                def heal_table(table_name, columns_to_add):
                    res = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"))
                    existing_cols = [r[0] for r in res.fetchall()]
                    
                    if existing_cols:
                        for col_name, sql_type in columns_to_add.items():
                            if col_name not in existing_cols:
                                logger.info(f"Healing: Adding column '{col_name}' to '{table_name}'...")
                                try:
                                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {sql_type}"))
                                except Exception as col_e:
                                    logger.error(f"Failed to add column {col_name} to {table_name}: {col_e}")
                        conn.commit()

                # Heal 'cover_letters'
                heal_table("cover_letters", {
                    "processing_status": "processingstatus DEFAULT 'PENDING'",
                    "gap_analysis": "JSON",
                    "job_analysis": "JSON"
                })
                
                # Heal 'portfolios'
                heal_table("portfolios", {
                    "processing_status": "processingstatus DEFAULT 'PENDING'",
                    "embedding": "vector(1024)"
                })

                # Heal 'recruitments'
                heal_table("recruitments", {
                    "view_count": "INTEGER DEFAULT 0",
                    "embedding": "vector(1024)",
                    "tags": "JSON"
                })
        except Exception as e:
            logger.error(f"Column healing failed: {e}")

        logger.info("Database initialization finished successfully.")
    except Exception as e:
        logger.error("Database initialization encountered a critical error:")
        logger.error(traceback.format_exc())
    finally:
        ddl_engine.dispose()
