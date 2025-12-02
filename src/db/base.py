from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.settings import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False, future=True,
    pool_pre_ping=True, # test connections before using them, avoid stale connections
    pool_size=10,       # max persistent connections in the pool
    max_overflow=5,     # allow temporary extra connections
    pool_timeout=30,    # wait max 30s for a connection
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

def get_session():
    return SessionLocal()
