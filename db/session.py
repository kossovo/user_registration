from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.configs import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
