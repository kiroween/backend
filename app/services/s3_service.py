import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional
from app.core.config import env_config

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=env_config.aws_access_key_id,
            aws_secret_access_key=env_config.aws_secret_access_key,
            region_name=env_config.aws_region
        )
        self.bucket_name = env_config.s3_bucket_name
    
    def upload_audio(self, file_content: bytes, file_name: str) -> Optional[str]:
        """
        S3에 오디오 파일을 업로드하고 URL을 반환합니다.
        
        Args:
            file_content: 업로드할 파일의 바이너리 데이터
            file_name: S3에 저장될 파일명
        
        Returns:
            업로드된 파일의 S3 URL, 실패 시 None
        """
        try:
            # S3에 파일 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_content,
                ContentType='audio/mpeg'
            )
            
            # S3 URL 생성
            url = f"https://{self.bucket_name}.s3.{env_config.aws_region}.amazonaws.com/{file_name}"
            logger.info(f"✅ S3 upload successful: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return None
    
    def delete_audio(self, file_name: str) -> bool:
        """
        S3에서 오디오 파일을 삭제합니다.
        
        Args:
            file_name: 삭제할 파일명
        
        Returns:
            성공 여부
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            logger.info(f"✅ S3 delete successful: {file_name}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ S3 delete failed: {e}")
            return False
