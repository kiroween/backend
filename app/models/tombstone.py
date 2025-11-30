from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Tombstone(Base):
    __tablename__ = "tombstones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=1, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    unlock_date = Column(Date, nullable=False, index=True)
    is_unlocked = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
