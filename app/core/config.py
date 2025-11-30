import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/timegrave.db")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # App
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # AWS S3 설정
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "ap-northeast-2")
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "timegrave-audio")
    
    # Supertone TTS API 설정
    supertone_api_key: str = os.getenv("SUPERTONE_API_KEY", "")
    supertone_api_url: str = os.getenv("SUPERTONE_API_URL", "")
    
    class Config:
        env_file = ".env"
        extra = "allow"  # 추가 필드 허용


env_config = Settings()
