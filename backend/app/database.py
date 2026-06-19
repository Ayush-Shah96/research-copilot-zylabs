"""Database configuration and session management."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from app.config import settings
from app.models import Base
import logging

logger = logging.getLogger(__name__)

# Create engine based on database URL
if settings.DATABASE_URL.startswith("sqlite"):
    # For SQLite, use StaticPool to avoid threading issues
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.SQLALCHEMY_ECHO,
    )
else:
    # For PostgreSQL or other databases
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.SQLALCHEMY_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def drop_db() -> None:
    """Drop all database tables. Use with caution!"""
    Base.metadata.drop_all(bind=engine)
    logger.warning("Database tables dropped")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Manages database operations."""
    
    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return SessionLocal()
    
    @staticmethod
    def create_all() -> None:
        """Create all tables."""
        init_db()
    
    @staticmethod
    def drop_all() -> None:
        """Drop all tables."""
        drop_db()
    
    @staticmethod
    def execute_raw(query: str) -> None:
        """Execute raw SQL query."""
        with engine.begin() as connection:
            connection.execute(query)


# SQLite specific optimizations
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable foreign keys for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "drop_db",
    "DatabaseManager",
]
