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
        import json
        
        tombstones = self.repository.get_all(user_id)
        result = []
        
        for tombstone in tombstones:
            # Parse share list
            share_list = None
            if tombstone.share:
                try:
                    share_list = json.loads(tombstone.share)
                except:
                    share_list = None
            
            response_data = {
                "id": tombstone.id,
                "user_id": tombstone.user_id,
                "title": tombstone.title,
                "unlock_date": tombstone.unlock_date.isoformat(),
                "is_unlocked": tombstone.is_unlocked,
                "enroll": tombstone.enroll,
                "share": share_list,
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
        import json
        
        # Validate unlock date is in the future
        if data.unlock_date <= date.today():
            raise ValueError("Unlock date must be in the future")
        
        # Set enroll to current user if not specified
        enroll = data.enroll if data.enroll else data.user_id
        
        # Convert share list to JSON string
        share_json = None
        if data.share:
            share_json = json.dumps(data.share)
        
        # 묘비 생성 시에는 TTS를 생성하지 않음 (조회 시 생성)
        tombstone = self.repository.create(
            user_id=data.user_id,
            title=data.title,
            content=data.content,
            audio_url=None,
            unlock_date=data.unlock_date,
            enroll=enroll,
            share=share_json
        )
        
        days_remaining = (tombstone.unlock_date - date.today()).days
        
        # Parse share for response
        share_list = None
        if tombstone.share:
            try:
                share_list = json.loads(tombstone.share)
            except:
                share_list = None
        
        return TombstoneResponseDto(
            id=tombstone.id,
            user_id=tombstone.user_id,
            title=tombstone.title,
            unlock_date=tombstone.unlock_date.isoformat(),
            is_unlocked=tombstone.is_unlocked,
            days_remaining=days_remaining,
            enroll=tombstone.enroll,
            share=share_list,
            created_at=tombstone.created_at.isoformat(),
            updated_at=tombstone.updated_at.isoformat()
        )

    def get_tombstone(self, tombstone_id: int) -> Optional[TombstoneResponseDto]:
        """Get a single tombstone with content filtering based on unlock status"""
        import json
        
        tombstone = self.repository.get_by_id(tombstone_id)
        
        if not tombstone:
            return None
        
        # Parse share list
        share_list = None
        if tombstone.share:
            try:
                share_list = json.loads(tombstone.share)
            except:
                share_list = None
        
        response_data = {
            "id": tombstone.id,
            "user_id": tombstone.user_id,
            "title": tombstone.title,
            "unlock_date": tombstone.unlock_date.isoformat(),
            "is_unlocked": tombstone.is_unlocked,
            "enroll": tombstone.enroll,
            "share": share_list,
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
    
    def update_share_list(self, tombstone_id: int, user_id: int, action: str, target_user_id: int) -> TombstoneResponseDto:
        """Add or remove a user from the share list"""
        import json
        
        tombstone = self.repository.get_by_id(tombstone_id)
        
        if not tombstone:
            raise ValueError("Tombstone not found")
        
        # Check ownership
        if tombstone.user_id != user_id:
            raise ValueError("You don't have permission to modify this tombstone")
        
        # Parse current share list
        current_share = []
        if tombstone.share:
            try:
                current_share = json.loads(tombstone.share)
            except:
                current_share = []
        
        # Update share list
        if action == "add":
            if target_user_id not in current_share:
                current_share.append(target_user_id)
        elif action == "remove":
            if target_user_id in current_share:
                current_share.remove(target_user_id)
        else:
            raise ValueError("Invalid action. Use 'add' or 'remove'")
        
        # Save updated share list
        share_json = json.dumps(current_share)
        self.repository.update_share_list(tombstone_id, share_json)
        
        # Return updated tombstone
        return self.get_tombstone(tombstone_id)
    
    def generate_invite_token(self, tombstone_id: int, user_id: int) -> Optional[str]:
        """Generate an invite token for a tombstone"""
        import uuid
        
        tombstone = self.repository.get_by_id(tombstone_id)
        
        if not tombstone:
            return None
        
        # Check ownership
        if tombstone.user_id != user_id:
            raise ValueError("You don't have permission to create invite link for this tombstone")
        
        # Generate unique UUID token
        invite_token = str(uuid.uuid4())
        
        # Update tombstone with invite token
        self.repository.update_invite_token(tombstone_id, invite_token)
        
        return invite_token
    
    def accept_invite(self, invite_token: str, user_id: int) -> TombstoneResponseDto:
        """Accept an invite and add user to share list"""
        import json
        
        tombstone = self.repository.get_by_invite_token(invite_token)
        
        if not tombstone:
            raise ValueError("Invalid invite token")
        
        # Parse current share list
        current_share = []
        if tombstone.share:
            try:
                current_share = json.loads(tombstone.share)
            except:
                current_share = []
        
        # Add user to share list if not already there
        if user_id not in current_share:
            current_share.append(user_id)
            share_json = json.dumps(current_share)
            self.repository.update_share_list(tombstone.id, share_json)
        
        # Return updated tombstone
        return self.get_tombstone(tombstone.id)
