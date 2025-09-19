from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:postgres@db:5432/minio_relay')
SessionLocal = sessionmaker(autoflush=True, bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()