from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.models.tombstone import Base, get_kst_now


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=get_kst_now, nullable=False)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False)
