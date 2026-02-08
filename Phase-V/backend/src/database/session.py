from sqlmodel import Session
from typing import Generator
from .engine import get_engine

def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(get_engine()) as session:
        yield session