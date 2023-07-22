from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy import create_engine
from app.config import settings

SQL_ALCHEMY_URL = f'{settings.db_connection}://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'

engine = create_engine(SQL_ALCHEMY_URL)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()