from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.user import User
from app.services.tombstone_service import TombstoneService
from app.schemas.tombstone import CreateTombstoneDto, TombstoneResponseDto
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/graves", tags=["graves"])


@router.get(
    "",
    summary="묘비 목록 조회",
    description="인증된 사용자의 모든 묘비 목록을 조회합니다. 잠금 상태와 관계없이 제목만 표시됩니다.",
    response_description="묘비 목록",
    responses={
        200: {
            "description": "성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "result": [
                                {
                                    "id": 1,
                                    "user_id": 1,
                                    "title": "나의 사랑하는 친구들에게",
                                    "unlock_date": "2025-12-01",
                                    "is_unlocked": True,
                                    "created_at": "2025-11-01T10:00:00",
                                    "updated_at": "2025-12-01T00:00:00"
                                },
                                {
                                    "id": 2,
                                    "user_id": 1,
                                    "title": "1년 후의 나에게",
                                    "unlock_date": "2026-12-01",
                                    "is_unlocked": False,
                                    "days_remaining": 365,
                                    "created_at": "2025-12-01T10:00:00",
                                    "updated_at": "2025-12-01T10:00:00"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
def list_graves(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 묘비 목록 조회
    
    인증된 사용자의 모든 묘비를 조회합니다.
    
    ### 응답 내용
    - 잠금 상태: `title`, `days_remaining` 포함
    - 잠금 해제 상태: `title`만 포함 (content는 상세 조회 시에만)
    
    ### 인증
    - Bearer Token 필요
    """
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="묘비 생성",
    description="새로운 디지털 타임캡슐(묘비)을 생성합니다. 설정한 날짜에 자동으로 잠금 해제됩니다.",
    response_description="생성된 묘비 정보",
    responses={
        201: {
            "description": "생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": 201,
                        "data": {
                            "result": {
                                "id": 1,
                                "user_id": 1,
                                "title": "나의 사랑하는 친구들에게",
                                "unlock_date": "2026-12-01",
                                "is_unlocked": False,
                                "days_remaining": 365,
                                "created_at": "2025-12-01T10:00:00",
                                "updated_at": "2025-12-01T10:00:00"
                            },
                            "response": "기억이 안전하게 봉인되었습니다. 365일 후에 다시 만나요."
                        }
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "status": 400,
                        "error": {
                            "message": "Unlock date must be in the future"
                        }
                    }
                }
            }
        }
    }
)
def create_grave(
    data: CreateTombstoneDto,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 묘비 생성
    
    새로운 디지털 타임캡슐을 생성합니다.
    
    ### 동작 방식
    1. 묘비 생성 (잠금 상태)
    2. `unlock_date`에 자동으로 잠금 해제
    3. 잠금 해제 후 첫 조회 시 TTS 음성 자동 생성
    
    ### 제약사항
    - `unlock_date`는 미래 날짜여야 함
    - `title`: 1-255자
    - `content`: 1자 이상
    
    ### 인증
    - Bearer Token 필요
    """
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


@router.get(
    "/{grave_id}",
    summary="묘비 상세 조회",
    description="특정 묘비의 상세 정보를 조회합니다. 잠금 해제된 경우 content와 TTS 음성 URL이 포함됩니다.",
    response_description="묘비 상세 정보",
    responses={
        200: {
            "description": "성공 - 잠금 해제된 경우",
            "content": {
                "application/json": {
                    "examples": {
                        "unlocked": {
                            "summary": "잠금 해제 상태",
                            "value": {
                                "status": 200,
                                "data": {
                                    "result": {
                                        "id": 1,
                                        "user_id": 1,
                                        "title": "나의 사랑하는 친구들에게",
                                        "content": "안녕, 미래의 나야. 오늘은 2025년 12월 1일이야. 1년 후의 너는 어떤 모습일까?",
                                        "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1_1_1733011200.123.mp3",
                                        "unlock_date": "2025-12-01",
                                        "is_unlocked": True,
                                        "created_at": "2025-11-01T10:00:00",
                                        "updated_at": "2025-12-01T00:00:00"
                                    }
                                }
                            }
                        },
                        "locked": {
                            "summary": "잠금 상태",
                            "value": {
                                "status": 200,
                                "data": {
                                    "result": {
                                        "id": 2,
                                        "user_id": 1,
                                        "title": "1년 후의 나에게",
                                        "unlock_date": "2026-12-01",
                                        "is_unlocked": False,
                                        "days_remaining": 365,
                                        "created_at": "2025-12-01T10:00:00",
                                        "updated_at": "2025-12-01T10:00:00"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "묘비를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "error": {
                            "message": "Grave not found"
                        }
                    }
                }
            }
        },
        403: {
            "description": "권한 없음",
            "content": {
                "application/json": {
                    "example": {
                        "status": 403,
                        "error": {
                            "code": "ACCESS_DENIED",
                            "message": "이 묘지에 접근할 권한이 없습니다."
                        }
                    }
                }
            }
        }
    }
)
def get_grave(
    grave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 묘비 상세 조회
    
    특정 묘비의 상세 정보를 조회합니다.
    
    ### 응답 내용
    
    **잠금 상태:**
    - `title`, `days_remaining` 포함
    - `content`, `audio_url` 제외
    
    **잠금 해제 상태:**
    - `title`, `content`, `audio_url` 포함
    - TTS 음성이 없으면 자동 생성 후 S3 업로드
    - 이후 조회 시 저장된 `audio_url` 재사용
    
    ### 권한
    - 본인의 묘비만 조회 가능
    
    ### 인증
    - Bearer Token 필요
    """
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


@router.post(
    "/unlock-check",
    status_code=status.HTTP_200_OK,
    summary="수동 잠금 해제 체크 (테스트용)",
    description="잠금 해제 스케줄러를 수동으로 실행합니다. 개발/테스트 환경에서 사용합니다.",
    response_description="잠금 해제된 묘비 개수"
)
def manual_unlock_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 수동 잠금 해제 체크
    
    스케줄러를 수동으로 실행하여 잠금 해제 대상 묘비를 확인합니다.
    
    ### 동작 방식
    - `unlock_date <= 오늘` 인 묘비들을 `is_unlocked = true`로 변경
    - 자정 스케줄러와 동일한 로직
    
    ### 용도
    - 개발/테스트 환경에서 즉시 확인
    - 관리자가 수동으로 실행
    
    ### 인증
    - Bearer Token 필요
    
    ### 주의
    - 프로덕션에서는 매일 자정에 자동 실행됨
    """
    try:
        service = TombstoneService(db)
        unlocked_count = service.check_and_unlock_tombstones()
        
        return {
            "status": 200,
            "data": {
                "result": {
                    "unlocked_count": unlocked_count,
                    "message": f"{unlocked_count}개의 묘비가 잠금 해제되었습니다."
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )



@router.post(
    "/{grave_id}/share",
    summary="묘비 공유 링크 생성",
    description="묘비를 친구에게 공유할 수 있는 링크를 생성합니다.",
    response_description="공유 링크 정보",
    responses={
        200: {
            "description": "성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "result": {
                                "share_url": "https://timegrave.com/shared/abc123xyz",
                                "share_token": "abc123xyz",
                                "expires_at": None
                            },
                            "message": "공유 링크가 생성되었습니다. 친구에게 전달하세요!"
                        }
                    }
                }
            }
        },
        404: {
            "description": "묘비를 찾을 수 없음"
        },
        403: {
            "description": "권한 없음"
        }
    }
)
def create_share_link(
    grave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 묘비 공유 링크 생성
    
    친구에게 공유할 수 있는 링크를 생성합니다.
    
    ### 동작 방식
    1. 고유한 share_token 생성
    2. 공유 URL 반환
    3. 친구가 링크를 통해 묘비 확인 가능
    
    ### 권한
    - 본인의 묘비만 공유 가능
    
    ### 인증
    - Bearer Token 필요
    """
    try:
        service = TombstoneService(db)
        share_token = service.generate_share_token(grave_id, current_user.id)
        
        if not share_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": 404, "error": {"message": "Grave not found"}}
            )
        
        # TODO: 실제 프론트엔드 URL로 변경 필요
        share_url = f"https://timegrave.com/shared/{share_token}"
        
        return {
            "status": 200,
            "data": {
                "result": {
                    "share_url": share_url,
                    "share_token": share_token,
                    "expires_at": None
                },
                "message": "공유 링크가 생성되었습니다. 친구에게 전달하세요!"
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": 403, "error": {"message": str(e)}}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )


@router.get(
    "/shared/{share_token}",
    summary="공유된 묘비 조회",
    description="공유 링크를 통해 묘비를 조회합니다. 회원가입이 필요합니다.",
    response_description="공유된 묘비 정보",
    responses={
        200: {
            "description": "성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "result": {
                                "id": 1,
                                "title": "나의 사랑하는 친구들에게",
                                "content": "안녕, 미래의 나야...",
                                "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1.mp3",
                                "unlock_date": "2025-12-01",
                                "is_unlocked": True,
                                "created_at": "2025-11-01T10:00:00",
                                "author_username": "홍길동"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "유효하지 않은 공유 링크"
        },
        403: {
            "description": "아직 잠금 해제되지 않은 묘비"
        }
    }
)
def view_shared_grave(
    share_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 공유된 묘비 조회
    
    친구가 공유 링크를 통해 묘비를 확인합니다.
    
    ### 동작 방식
    1. 회원가입/로그인 필수
    2. share_token으로 묘비 조회
    3. 잠금 해제된 묘비만 조회 가능
    
    ### 제약사항
    - 잠금 해제된 묘비만 공유 가능
    - 회원가입 필수
    
    ### 인증
    - Bearer Token 필요
    """
    try:
        service = TombstoneService(db)
        tombstone = service.get_tombstone_by_share_token(share_token)
        
        if not tombstone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": 404, "error": {"message": "유효하지 않은 공유 링크입니다."}}
            )
        
        if not tombstone.is_unlocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"status": 403, "error": {"message": "아직 잠금 해제되지 않은 묘비입니다."}}
            )
        
        # Get author username
        from app.models.user import User as UserModel
        author = db.query(UserModel).filter(UserModel.id == tombstone.user_id).first()
        author_username = author.username if author else "Unknown"
        
        return {
            "status": 200,
            "data": {
                "result": {
                    "id": tombstone.id,
                    "title": tombstone.title,
                    "content": tombstone.content,
                    "audio_url": tombstone.audio_url,
                    "unlock_date": tombstone.unlock_date.isoformat(),
                    "is_unlocked": tombstone.is_unlocked,
                    "created_at": tombstone.created_at.isoformat(),
                    "author_username": author_username
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )


@router.post(
    "/shared/{share_token}/copy",
    status_code=status.HTTP_201_CREATED,
    summary="공유된 묘비를 내 계정에 저장",
    description="친구가 공유한 묘비를 내 계정에 복사합니다.",
    response_description="복사된 묘비 정보",
    responses={
        201: {
            "description": "성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": 201,
                        "data": {
                            "result": {
                                "id": 5,
                                "user_id": 2,
                                "title": "[공유받음] 나의 사랑하는 친구들에게",
                                "content": "안녕, 미래의 나야...",
                                "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1.mp3",
                                "unlock_date": "2025-12-01",
                                "is_unlocked": True,
                                "created_at": "2025-12-02T15:30:00",
                                "updated_at": "2025-12-02T15:30:00"
                            },
                            "message": "친구의 묘비가 내 계정에 저장되었습니다."
                        }
                    }
                }
            }
        },
        404: {
            "description": "유효하지 않은 공유 링크"
        },
        403: {
            "description": "아직 잠금 해제되지 않은 묘비"
        }
    }
)
def copy_shared_grave(
    share_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 공유된 묘비 복사
    
    친구가 공유한 묘비를 내 계정에 저장합니다.
    
    ### 동작 방식
    1. share_token으로 원본 묘비 조회
    2. 내 계정에 복사본 생성
    3. 제목에 "[공유받음]" 접두사 추가
    4. 동일한 audio_url 재사용
    
    ### 제약사항
    - 잠금 해제된 묘비만 복사 가능
    - 회원가입 필수
    
    ### 인증
    - Bearer Token 필요
    """
    try:
        service = TombstoneService(db)
        copied_tombstone = service.copy_shared_tombstone(share_token, current_user.id)
        
        return {
            "status": 201,
            "data": {
                "result": copied_tombstone.model_dump(exclude_none=True),
                "message": "친구의 묘비가 내 계정에 저장되었습니다."
            }
        }
    except ValueError as e:
        error_msg = str(e)
        if "Invalid share token" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": 404, "error": {"message": "유효하지 않은 공유 링크입니다."}}
            )
        elif "not yet unlocked" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"status": 403, "error": {"message": error_msg}}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"status": 400, "error": {"message": error_msg}}
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )
