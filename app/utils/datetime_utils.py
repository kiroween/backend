"""DateTime utility functions for timezone-aware operations"""
from datetime import datetime, timezone, timedelta

# 한국 시간대 (UTC+9)
KST = timezone(timedelta(hours=9))


def now_kst() -> datetime:
    """현재 한국 시간을 반환합니다 (timezone-aware)"""
    return datetime.now(KST)


def utc_to_kst(dt: datetime) -> datetime:
    """UTC datetime을 KST로 변환합니다"""
    if dt.tzinfo is None:
        # naive datetime을 UTC로 간주
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST)


def kst_to_utc(dt: datetime) -> datetime:
    """KST datetime을 UTC로 변환합니다"""
    if dt.tzinfo is None:
        # naive datetime을 KST로 간주
        dt = dt.replace(tzinfo=KST)
    return dt.astimezone(timezone.utc)
