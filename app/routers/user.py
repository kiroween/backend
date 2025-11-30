from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserSignUpDto, UserSignInDto
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다.",
    response_description="생성된 사용자 정보",
    responses={
        201: {
            "description": "회원가입 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": 201,
                        "data": {
                            "result": {
                                "id": 1,
                                "email": "user@example.com",
                                "username": "김타임",
                                "created_at": "2025-12-01T10:00:00"
                            },
                            "message": "환영합니다, 김타임님. TimeGrave에 오신 것을 환영합니다."
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
                            "code": "EMAIL_ALREADY_EXISTS",
                            "message": "이미 사용 중인 이메일입니다."
                        }
                    }
                }
            }
        }
    }
)
def sign_up(data: UserSignUpDto, db: Session = Depends(get_db)):
    """
    ## 회원가입
    
    새로운 사용자 계정을 생성합니다.
    
    ### 제약사항
    - 이메일: 유효한 이메일 형식
    - 비밀번호: 8-72자
    - 사용자 이름: 1-100자
    
    ### 오류 코드
    - `EMAIL_ALREADY_EXISTS`: 이미 사용 중인 이메일
    - `VALIDATION_ERROR`: 입력값 검증 실패
    """
    try:
        service = UserService(db)
        user = service.sign_up(data)
        
        return {
            "status": 201,
            "data": {
                "result": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "created_at": user.created_at
                },
                "message": f"환영합니다, {user.username}님. TimeGrave에 오신 것을 환영합니다."
            }
        }
    except ValueError as e:
        error_message = str(e)
        # Determine error code based on error message
        if "이미 사용 중인 이메일" in error_message:
            error_code = "EMAIL_ALREADY_EXISTS"
        else:
            error_code = "VALIDATION_ERROR"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": 400, "error": {"code": error_code, "message": error_message}}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": 400, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}
        )


@router.post(
    "/sign-in",
    summary="로그인",
    description="이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.",
    response_description="JWT 토큰 및 사용자 정보",
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "result": {
                                "user": {
                                    "id": 1,
                                    "email": "user@example.com",
                                    "username": "김타임"
                                },
                                "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzMzMDExMjAwfQ.example",
                                "expires_at": "2025-12-01T10:30:00"
                            },
                            "message": "다시 돌아오신 것을 환영합니다."
                        }
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "content": {
                "application/json": {
                    "example": {
                        "status": 401,
                        "error": {
                            "code": "INVALID_CREDENTIALS",
                            "message": "이메일 또는 비밀번호가 일치하지 않습니다."
                        }
                    }
                }
            }
        }
    }
)
def sign_in(data: UserSignInDto, db: Session = Depends(get_db)):
    """
    ## 로그인
    
    이메일과 비밀번호로 인증하여 JWT 세션 토큰을 발급받습니다.
    
    ### 응답
    - `session_token`: JWT 토큰 (Bearer 인증에 사용)
    - `expires_at`: 토큰 만료 시간
    - `user`: 사용자 정보
    
    ### 토큰 사용
    ```
    Authorization: Bearer {session_token}
    ```
    
    ### 오류 코드
    - `INVALID_CREDENTIALS`: 이메일 또는 비밀번호 불일치
    """
    try:
        service = UserService(db)
        token_data = service.sign_in(data)
        
        return {
            "status": 200,
            "data": {
                "result": {
                    "user": {
                        "id": token_data.user.id,
                        "email": token_data.user.email,
                        "username": token_data.user.username
                    },
                    "session_token": token_data.session_token,
                    "expires_at": token_data.expires_at
                },
                "message": "다시 돌아오신 것을 환영합니다."
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": 401, "error": {"code": "INVALID_CREDENTIALS", "message": str(e)}}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )


@router.post(
    "/sign-out",
    summary="로그아웃",
    description="현재 세션을 종료합니다.",
    response_description="로그아웃 성공 메시지"
)
def sign_out(current_user: User = Depends(get_current_user)):
    """
    ## 로그아웃
    
    현재 세션을 종료합니다.
    
    ### 인증
    - Bearer Token 필요
    
    ### 참고
    - JWT는 stateless이므로 서버에서 토큰을 무효화하지 않음
    - 클라이언트에서 토큰을 삭제해야 함
    """
    return {
        "status": 200,
        "data": {
            "message": "안전하게 로그아웃되었습니다. 다음에 또 만나요."
        }
    }


@router.delete(
    "",
    summary="회원탈퇴",
    description="사용자 계정과 모든 묘비를 영구적으로 삭제합니다.",
    response_description="삭제 완료 메시지"
)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ## 회원탈퇴
    
    사용자 계정과 모든 관련 데이터를 영구적으로 삭제합니다.
    
    ### 삭제되는 데이터
    - 사용자 계정
    - 모든 묘비 (잠금 상태와 관계없이)
    
    ### 주의
    - 이 작업은 되돌릴 수 없습니다
    - 모든 기억이 영원히 사라집니다
    
    ### 인증
    - Bearer Token 필요
    """
    try:
        service = UserService(db)
        deleted_graves_count = service.delete_account(current_user.id)
        
        return {
            "status": 200,
            "data": {
                "message": "계정이 영원히 삭제되었습니다. 모든 기억이 함께 사라집니다.",
                "deleted_graves_count": deleted_graves_count
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": 500, "error": {"message": str(e)}}
        )
