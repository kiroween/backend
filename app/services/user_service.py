from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.tombstone_repository import TombstoneRepository
from app.schemas.user import UserSignUpDto, UserSignInDto, UserResponseDto, TokenResponseDto
from app.utils.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_HOURS


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.tombstone_repository = TombstoneRepository(db)

    def sign_up(self, data: UserSignUpDto) -> UserResponseDto:
        """회원가입"""
        # 이메일 중복 확인
        existing_user = self.user_repository.get_by_email(data.email)
        if existing_user:
            raise ValueError("이미 사용 중인 이메일입니다.")
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(data.password)
        
        # 사용자 생성
        user = self.user_repository.create(
            email=data.email,
            username=data.username,
            hashed_password=hashed_password
        )
        
        return UserResponseDto(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at.isoformat()
        )

    def sign_in(self, data: UserSignInDto) -> TokenResponseDto:
        """로그인"""
        # 사용자 조회
        user = self.user_repository.get_by_email(data.email)
        if not user:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        
        # 비밀번호 검증
        if not verify_password(data.password, user.hashed_password):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        
        # JWT 토큰 생성
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        expires_at = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        return TokenResponseDto(
            user=UserResponseDto(
                id=user.id,
                email=user.email,
                username=user.username,
                created_at=user.created_at.isoformat()
            ),
            session_token=access_token,
            expires_at=expires_at.isoformat() + "Z"
        )

    def delete_account(self, user_id: int) -> int:
        """회원탈퇴 - 사용자와 관련된 모든 묘지 삭제"""
        # 사용자의 모든 묘지 조회
        graves = self.tombstone_repository.get_all(user_id)
        graves_count = len(graves)
        
        # 묘지 삭제
        for grave in graves:
            self.db.delete(grave)
        
        # 사용자 삭제
        self.user_repository.delete(user_id)
        
        return graves_count
