from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserSignUpDto, UserSignInDto
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
def sign_up(data: UserSignUpDto, db: Session = Depends(get_db)):
    """회원가입"""
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


@router.post("/sign-in")
def sign_in(data: UserSignInDto, db: Session = Depends(get_db)):
    """로그인"""
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


@router.post("/sign-out")
def sign_out(current_user: User = Depends(get_current_user)):
    """로그아웃"""
    return {
        "status": 200,
        "data": {
            "message": "안전하게 로그아웃되었습니다. 다음에 또 만나요."
        }
    }


@router.delete("")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """회원탈퇴"""
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
