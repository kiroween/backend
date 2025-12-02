from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from app.utils.datetime_utils import now_kst

Base = declarative_base()


def get_kst_now():
    """한국 시간을 naive datetime으로 반환 (SQLite 호환)"""
    return now_kst().replace(tzinfo=None)


class Tombstone(Base):
    __tablename__ = "tombstones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=1, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    audio_url = Column(String(500), nullable=True)  # S3 오디오 파일 URL
    unlock_date = Column(Date, nullable=False, index=True)
    is_unlocked = Column(Boolean, default=False, index=True)
    share_token = Column(String(100), nullable=True, unique=True, index=True)  # 공유 링크용 토큰
    created_at = Column(DateTime, default=get_kst_now, nullable=False)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False)
