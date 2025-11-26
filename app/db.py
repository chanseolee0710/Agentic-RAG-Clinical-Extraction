# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

# Base class that all ORM models will inherit from
Base = declarative_base()

# Create the SQLAlchemy engine using the config DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

# Factory that will create new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database.

    This imports the models module so that SQLAlchemy is aware of all
    mapped classes, then creates all tables in the database if they
    don't exist yet.
    """
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency for FastAPI routes.

    Yields a database session that opens at the beginning, 
    and closes automatically when request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
