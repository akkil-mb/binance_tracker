import structlog
from app import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

logger = structlog.get_logger(__name__)

DATABASE_URL = settings.BaseSettings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=100,
    max_overflow=20,
    pool_recycle=1800,
    pool_timeout=30,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()