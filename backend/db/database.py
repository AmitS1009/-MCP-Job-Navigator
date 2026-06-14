import logging
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Async SQLAlchemy engine
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

# AsyncSessionLocal session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base for declarative models
Base = declarative_base()

async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Logs entry and exit.
    """
    logger.info("[DB] Initializing database...")
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("[DB] Database initialized successfully.")
    except Exception as e:
        logger.error(f"[DB] Failed to initialize database: {e}")
        raise