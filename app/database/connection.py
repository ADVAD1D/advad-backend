import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import settings
from app.models.base import Base

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Ensure psycopg2 is used with SQLAlchemy's postgresql dialect
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    db_url, 
    pool_pre_ping=True,  # Useful for handling disconnected connections
    pool_size=10, 
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        # Import models here to ensure they are registered with Base.metadata before create_all
        import app.models.phase_record
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing DB: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize tables when this module is imported (keeps original behavior)
init_db()
