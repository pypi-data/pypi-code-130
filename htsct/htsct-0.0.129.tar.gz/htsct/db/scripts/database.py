from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from htsct.constants import SQLALCHEMY_DATABASE_URL


# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
class DB:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()


def get_db():
    db = DB.SessionLocal()
    try:
        yield db
    finally:
        db.close()
