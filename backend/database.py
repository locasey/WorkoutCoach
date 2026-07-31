from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/workoutcoach')

# Create engine
# pool_pre_ping: test each pooled connection with a lightweight query before use and
# transparently reconnect if it's dead — Neon (serverless Postgres) silently closes idle
# connections, which otherwise surfaces as "SSL connection has been closed unexpectedly"
# on the first query after any idle period.
# pool_recycle: proactively recycle connections older than 5 minutes as a second safeguard.
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=300)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables - use with caution!"""
    Base.metadata.drop_all(bind=engine)

