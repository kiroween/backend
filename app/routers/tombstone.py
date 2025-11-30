from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.user import User
from app.services.tombstone_service import TombstoneService
from app.schemas.tombstone import CreateTombstoneDto, TombstoneResponseDto
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/graves", tags=["graves"])


@router.get("")
def list_graves(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all graves for the authenticated user"""
    try:
        service = TombstoneService(db)
        tombstones = service.list_tombstones(user_id=current_user.id)
        
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


@router.post("", status_code=status.HTTP_201_CREATED)
def create_grave(
    data: CreateTombstoneDto,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new grave for the authenticated user"""
    try:
        # Override user_id with authenticated user's id
        data.user_id = current_user.id
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


@router.get("/{grave_id}")
def get_grave(
    grave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific grave by ID for the authenticated user"""
    try:
        service = TombstoneService(db)
        tombstone = service.get_tombstone(grave_id)
        
        if not tombstone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": 404, "error": {"message": "Grave not found"}}
            )
        
        # Check if the grave belongs to the authenticated user
        if tombstone.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"status": 403, "error": {"code": "ACCESS_DENIED", "message": "이 묘지에 접근할 권한이 없습니다."}}
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
