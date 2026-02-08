"""Script to drop and recreate all tables."""
import os
from dotenv import load_dotenv

# Load environment variables from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Drop tables in correct order (respecting foreign keys)
    conn.execute(text("DROP TABLE IF EXISTS tasktaglink CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS tag CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS task CASCADE"))
    conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))

    # Drop enum types
    conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
    conn.execute(text("DROP TYPE IF EXISTS taskstatus CASCADE"))
    conn.execute(text("DROP TYPE IF EXISTS taskpriority CASCADE"))
    conn.execute(text("DROP TYPE IF EXISTS recurrencerule CASCADE"))

    conn.commit()
    print("All tables and types dropped successfully!")
