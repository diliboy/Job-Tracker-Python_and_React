from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.config import settings

# Create database engine
# Similar to DataSource configuration in Spring Boot
engine = create_engine(
    settings.database_url,
    # For SQLite, we need to enable check_same_thread=False
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,  # Log SQL queries when debug=True
    pool_pre_ping=True,  # Verify connections before using them
)

# Session factory
# Similar to EntityManagerFactory in JPA
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
# Similar to @Entity base class in JPA
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    
    from app.models import user, job_application, documents 
    Base.metadata.create_all(bind=engine)