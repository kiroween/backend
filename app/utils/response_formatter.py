from typing import Any, Optional


def format_success_response(status_code: int, result: Any, message: Optional[str] = None) -> dict:
    """Format a successful API response"""
    response = {
        "status": status_code,
        "data": {
            "result": result
        }
    }
    
    if message:
        response["data"]["response"] = message
    
    return response


def format_error_response(status_code: int, message: str) -> dict:
    """Format an error API response"""
    return {
        "status": status_code,
        "error": {
            "message": message
        }
    }


def generate_creation_message(days_remaining: int) -> str:
    """Generate user-friendly message for tombstone creation"""
    return f"기억이 안전하게 봉인되었습니다. {days_remaining}일 후에 다시 만나요."
