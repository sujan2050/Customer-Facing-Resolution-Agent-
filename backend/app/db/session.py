import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("skyroute.db")

database_url = settings.DATABASE_URL
connect_args = {}

# Test connection to configured DATABASE_URL; fallback to SQLite if unreachable
engine = None
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, echo=False, connect_args=connect_args)
else:
    try:
        test_engine = create_engine(database_url, echo=False, connect_args={"connect_timeout": 3}, pool_pre_ping=True)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = test_engine
        print(f"Connected successfully to PostgreSQL database: {database_url}")
    except Exception as e:
        print(f"Warning: PostgreSQL database not reachable ({e}). Falling back to local SQLite database: resolution_agent.db")
        database_url = "sqlite:///./resolution_agent.db"
        connect_args = {"check_same_thread": False}
        engine = create_engine(database_url, echo=False, connect_args=connect_args)

# Enable foreign keys for SQLite
if database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
