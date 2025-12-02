from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session
import logging
from app.models.tombstone import Tombstone
from app.repositories.tombstone_repository import TombstoneRepository
from app.schemas.tombstone import CreateTombstoneDto, TombstoneResponseDto
from app.services.tts_service import TTSService
from app.services.s3_service import S3Service

logger = logging.getLogger(__name__)


class TombstoneService:
    def __init__(self, db: Session):
        self.repository = TombstoneRepository(db)
        self.tts_service = TTSService()
        self.s3_service = S3Service()

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
        
        # 묘비 생성 시에는 TTS를 생성하지 않음 (조회 시 생성)
        tombstone = self.repository.create(
            user_id=data.user_id,
            title=data.title,
            content=data.content,
            audio_url=None,
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
            
            # 잠금 해제된 경우, audio_url이 없으면 TTS 생성
            if not tombstone.audio_url and tombstone.content:
                logger.info(f"🎙️ Generating TTS for tombstone {tombstone_id}")
                try:
                    # TTS 음성 생성
                    audio_bytes = self.tts_service.generate_audio(tombstone.content)
                    
                    if audio_bytes:
                        # S3에 업로드
                        from app.utils.datetime_utils import now_kst
                        timestamp = now_kst().timestamp()
                        file_name = f"tombstone_{tombstone.user_id}_{tombstone.id}_{timestamp}.mp3"
                        audio_url = self.s3_service.upload_audio(audio_bytes, file_name)
                        
                        if audio_url:
                            logger.info(f"✅ Audio uploaded successfully: {audio_url}")
                            # DB에 audio_url 저장
                            self.repository.update_audio_url(tombstone_id, audio_url)
                            response_data["audio_url"] = audio_url
                        else:
                            logger.warning("⚠️ S3 upload failed")
                            response_data["audio_url"] = None
                    else:
                        logger.warning("⚠️ TTS generation failed")
                        response_data["audio_url"] = None
                        
                except Exception as e:
                    logger.error(f"❌ Error during TTS/S3 process: {e}")
                    response_data["audio_url"] = None
            else:
                # 이미 audio_url이 있으면 그대로 사용
                response_data["audio_url"] = tombstone.audio_url
        else:
            days_remaining = (tombstone.unlock_date - date.today()).days
            response_data["days_remaining"] = days_remaining
        
        return TombstoneResponseDto(**response_data)

    def check_and_unlock_tombstones(self) -> int:
        """Check and unlock tombstones whose unlock date has arrived"""
        current_date = date.today()
        return self.repository.update_unlock_status(current_date)

    def generate_share_token(self, tombstone_id: int, user_id: int) -> Optional[str]:
        """Generate a share token for a tombstone"""
        import secrets
        
        tombstone = self.repository.get_by_id(tombstone_id)
        
        if not tombstone:
            return None
        
        # Check ownership
        if tombstone.user_id != user_id:
            raise ValueError("You don't have permission to share this tombstone")
        
        # Generate unique token
        share_token = secrets.token_urlsafe(16)
        
        # Update tombstone with share token
        self.repository.update_share_token(tombstone_id, share_token)
        
        return share_token
    
    def get_tombstone_by_share_token(self, share_token: str) -> Optional[Tombstone]:
        """Get tombstone by share token"""
        return self.repository.get_by_share_token(share_token)
    
    def copy_shared_tombstone(self, share_token: str, new_user_id: int) -> TombstoneResponseDto:
        """Copy a shared tombstone to another user's account"""
        # Get original tombstone
        original = self.repository.get_by_share_token(share_token)
        
        if not original:
            raise ValueError("Invalid share token")
        
        # Check if already unlocked
        if not original.is_unlocked:
            raise ValueError("This tombstone is not yet unlocked and cannot be shared")
        
        # Create a copy for the new user
        copied_tombstone = self.repository.create(
            user_id=new_user_id,
            title=f"[공유받음] {original.title}",
            content=original.content,
            audio_url=original.audio_url,  # Reuse the same audio URL
            unlock_date=original.unlock_date
        )
        
        # Mark as unlocked since it's a copy of an unlocked tombstone
        self.repository.update_unlock_status_by_id(copied_tombstone.id, True)
        
        return TombstoneResponseDto(
            id=copied_tombstone.id,
            user_id=copied_tombstone.user_id,
            title=copied_tombstone.title,
            content=copied_tombstone.content,
            audio_url=copied_tombstone.audio_url,
            unlock_date=copied_tombstone.unlock_date.isoformat(),
            is_unlocked=True,
            created_at=copied_tombstone.created_at.isoformat(),
            updated_at=copied_tombstone.updated_at.isoformat()
        )
