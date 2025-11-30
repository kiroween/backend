import requests
import logging
from typing import Optional
from app.core.config import env_config

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self):
        self.api_key = env_config.supertone_api_key
        self.api_url = env_config.supertone_api_url
    
    def generate_audio(self, text: str) -> Optional[bytes]:
        """
        Supertone API를 사용하여 TTS 음성을 생성합니다.
        
        Args:
            text: 변환할 텍스트
        
        Returns:
            음성 파일의 바이너리 데이터, 실패 시 None
        """
        logger.info("✅ TTS generation started")
        
        payload = {
            "text": text,
            "language": "ko",
            "style": "neutral"
        }
        
        headers = {
            "x-sup-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        request_url = self.api_url
        
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"❌ Supertone API failed: {response.status_code} - {response.text}")
                return None
            
            logger.info("✅ TTS generation successful")
            return response.content
            
        except Exception as e:
            logger.error(f"❌ TTS generation error: {e}")
            return None
