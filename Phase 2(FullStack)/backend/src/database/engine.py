from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL logging in development
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

def create_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

def get_engine():
    """Get the database engine."""
    return engine