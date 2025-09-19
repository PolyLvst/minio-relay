from datetime import datetime
import pytz
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False)
    minio_object_filename = Column(Text, nullable=False)
    uploader = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC)) # UTC