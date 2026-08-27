# This is where the SQLAlchemy engine, session, and Base live — the shared
# infrastructure every model and route depends on, but that isn't itself a
# model or a route.

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# --- Base -----------------------------------------------------------------
class Base(DeclarativeBase):
    pass

# --- Engine -----------------------------------------------------------------
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# --- Session ------------------------------------------------------------
SessionLocal = sessionmaker(bind=engine)
def get_db():
    with SessionLocal() as session:
        yield session