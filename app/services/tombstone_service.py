from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.tombstone import Tombstone
from app.repositories.tombstone_repository import TombstoneRepository
from app.schemas.tombstone import CreateTombstoneDto, TombstoneResponseDto


class TombstoneService:
    def __init__(self, db: Session):
        self.repository = TombstoneRepository(db)

    def list_tombstones(self, user_id: int = 1) -> List[TombstoneResponseDto]:
        """List all tombstones for a user - always shows only title, never content"""
        tombstones = self.repository.get_all(user_id)
        result = []
        
        for tombstone in tombstones:
            response_data = {
                "id": tombstone.id,
                "user_id": tombstone.user_id,
                "title": tombstone.title,
                "unlock_date": tombstone.unlock_date.isoformat(),
                "is_unlocked": tombstone.is_unlocked,
                "created_at": tombstone.created_at.isoformat(),
                "updated_at": tombstone.updated_at.isoformat()
            }
            
            # Always calculate days_remaining for list view, regardless of unlock status
            if not tombstone.is_unlocked:
                days_remaining = (tombstone.unlock_date - date.today()).days
                response_data["days_remaining"] = days_remaining
            
            # Never include content in list view
            
            result.append(TombstoneResponseDto(**response_data))
        
        return result

    def create_tombstone(self, data: CreateTombstoneDto) -> TombstoneResponseDto:
        """Create a new tombstone with validation"""
        # Validate unlock date is in the future
        if data.unlock_date <= date.today():
            raise ValueError("Unlock date must be in the future")
        
        tombstone = self.repository.create(
            user_id=data.user_id,
            title=data.title,
            content=data.content,
            unlock_date=data.unlock_date
        )
        
        days_remaining = (tombstone.unlock_date - date.today()).days
        
        return TombstoneResponseDto(
            id=tombstone.id,
            user_id=tombstone.user_id,
            title=tombstone.title,
            unlock_date=tombstone.unlock_date.isoformat(),
            is_unlocked=tombstone.is_unlocked,
            days_remaining=days_remaining,
            created_at=tombstone.created_at.isoformat(),
            updated_at=tombstone.updated_at.isoformat()
        )

    def get_tombstone(self, tombstone_id: int) -> Optional[TombstoneResponseDto]:
        """Get a single tombstone with content filtering based on unlock status"""
        tombstone = self.repository.get_by_id(tombstone_id)
        
        if not tombstone:
            return None
        
        response_data = {
            "id": tombstone.id,
            "user_id": tombstone.user_id,
            "title": tombstone.title,
            "unlock_date": tombstone.unlock_date.isoformat(),
            "is_unlocked": tombstone.is_unlocked,
            "created_at": tombstone.created_at.isoformat(),
            "updated_at": tombstone.updated_at.isoformat()
        }
        
        if tombstone.is_unlocked:
            response_data["content"] = tombstone.content
        else:
            days_remaining = (tombstone.unlock_date - date.today()).days
            response_data["days_remaining"] = days_remaining
        
        return TombstoneResponseDto(**response_data)

    def check_and_unlock_tombstones(self) -> int:
        """Check and unlock tombstones whose unlock date has arrived"""
        current_date = date.today()
        return self.repository.update_unlock_status(current_date)
