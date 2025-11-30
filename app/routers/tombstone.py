from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.services.tombstone_service import TombstoneService
from app.schemas.tombstone import CreateTombstoneDto, TombstoneResponseDto

router = APIRouter(prefix="/api", tags=["tombstones"])


@router.get("/graves")
def get_graveyard(db: Session = Depends(get_db)):
    """Get all tombstones for the user (graveyard dashboard)"""
    try:
        service = TombstoneService(db)
        tombstones = service.list_tombstones(user_id=1)
        
        return {
            "status": 200,
            "data": {
                "result": [tombstone.model_dump(exclude_none=True) for tombstone in tombstones]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )


@router.post("/tombstones", status_code=status.HTTP_201_CREATED)
def create_tombstone(data: CreateTombstoneDto, db: Session = Depends(get_db)):
    """Create a new tombstone"""
    try:
        service = TombstoneService(db)
        tombstone = service.create_tombstone(data)
        
        days_remaining = tombstone.days_remaining
        
        return {
            "status": 201,
            "data": {
                "result": tombstone.model_dump(exclude_none=True),
                "response": f"기억이 안전하게 봉인되었습니다. {days_remaining}일 후에 다시 만나요."
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": 400, "error": {"message": str(e)}}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )


@router.get("/tombstones/{tombstone_id}")
def get_tombstone(tombstone_id: int, db: Session = Depends(get_db)):
    """Get a specific tombstone by ID"""
    try:
        service = TombstoneService(db)
        tombstone = service.get_tombstone(tombstone_id)
        
        if not tombstone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": 404, "error": {"message": "Tombstone not found"}}
            )
        
        return {
            "status": 200,
            "data": {
                "result": tombstone.model_dump(exclude_none=True)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )
