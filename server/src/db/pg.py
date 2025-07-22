from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.lib.logger import logger
from src.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.postgres_connection_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # validates connections before use
    pool_recycle=300,  # recycle connections every 5 minutes
    echo=False,  # set to True for SQL query logging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Direct database session for non-FastAPI usage"""
    return SessionLocal()


def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute(text('SELECT 1'))
        db.close()
        logger.info("PostgreSQL connection test successful")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection test failed: {e}")
        return False
