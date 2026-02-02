from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
import os

# Load environment variables from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Configure engine based on database type
is_sqlite = "sqlite" in DATABASE_URL

engine_kwargs = {
    "echo": True,  # Enable SQL logging in development
}

if is_sqlite:
    from sqlalchemy.pool import StaticPool
    engine_kwargs["poolclass"] = StaticPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL settings for Neon serverless
    engine_kwargs["pool_pre_ping"] = True  # Check connection health

# Create database engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

def create_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

def get_engine():
    """Get the database engine."""
    return engine