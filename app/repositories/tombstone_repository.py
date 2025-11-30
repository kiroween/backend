from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.tombstone import Tombstone


class TombstoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int = 1) -> List[Tombstone]:
        """Get all tombstones for a user"""
        return self.db.query(Tombstone).filter(Tombstone.user_id == user_id).all()

    def get_by_id(self, tombstone_id: int) -> Optional[Tombstone]:
        """Get a single tombstone by ID"""
        return self.db.query(Tombstone).filter(Tombstone.id == tombstone_id).first()

    def create(self, user_id: int, title: str, content: str, unlock_date: date) -> Tombstone:
        """Create a new tombstone"""
        tombstone = Tombstone(
            user_id=user_id,
            title=title,
            content=content,
            unlock_date=unlock_date,
            is_unlocked=False
        )
        self.db.add(tombstone)
        self.db.commit()
        self.db.refresh(tombstone)
        return tombstone

    def update_unlock_status(self, current_date: date) -> int:
        """Update unlock status for tombstones whose unlock date has arrived"""
        result = self.db.query(Tombstone).filter(
            Tombstone.unlock_date <= current_date,
            Tombstone.is_unlocked == False
        ).update({"is_unlocked": True})
        self.db.commit()
        return result
