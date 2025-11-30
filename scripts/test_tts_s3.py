#!/usr/bin/env python3
"""
TTS 및 S3 연동 테스트 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tts_service import TTSService
from app.services.s3_service import S3Service


def test_tts():
    """TTS 서비스 테스트"""
    print("🧪 TTS 서비스 테스트 시작...")
    
    tts_service = TTSService()
    test_text = "안녕하세요. 이것은 테스트 메시지입니다."
    
    # TTS 음성 테스트
    print("\n1️⃣ TTS 음성 생성 중...")
    audio_bytes = tts_service.generate_audio(test_text)
    
    if audio_bytes:
        print(f"✅ 성공! 음성 파일 크기: {len(audio_bytes)} bytes")
        return True
    else:
        print("❌ 실패!")
        return False


def test_s3():
    """S3 서비스 테스트"""
    print("\n🧪 S3 서비스 테스트 시작...")
    
    s3_service = S3Service()
    test_content = b"This is a test audio file"
    test_filename = "test_audio.mp3"
    
    # 업로드 테스트
    print("\n1️⃣ S3 업로드 중...")
    url = s3_service.upload_audio(test_content, test_filename)
    
    if url:
        print(f"✅ 업로드 성공! URL: {url}")
    else:
        print("❌ 업로드 실패!")
        return False
    
    # 삭제 테스트
    print("\n2️⃣ S3 삭제 중...")
    success = s3_service.delete_audio(test_filename)
    
    if success:
        print("✅ 삭제 성공!")
    else:
        print("❌ 삭제 실패!")
        return False
    
    return True


def test_integration():
    """통합 테스트: TTS + S3"""
    print("\n🧪 통합 테스트 시작 (TTS + S3)...")
    
    tts_service = TTSService()
    s3_service = S3Service()
    
    test_text = "미래의 나에게 보내는 메시지입니다."
    
    # TTS 생성
    print("\n1️⃣ TTS 음성 생성 중...")
    audio_bytes = tts_service.generate_audio(test_text)
    
    if not audio_bytes:
        print("❌ TTS 생성 실패!")
        return False
    
    print(f"✅ TTS 생성 성공! 크기: {len(audio_bytes)} bytes")
    
    # S3 업로드
    print("\n2️⃣ S3 업로드 중...")
    test_filename = "integration_test_audio.mp3"
    url = s3_service.upload_audio(audio_bytes, test_filename)
    
    if not url:
        print("❌ S3 업로드 실패!")
        return False
    
    print(f"✅ S3 업로드 성공! URL: {url}")
    
    # 정리
    print("\n3️⃣ 테스트 파일 삭제 중...")
    s3_service.delete_audio(test_filename)
    print("✅ 정리 완료!")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("TTS 및 S3 연동 테스트")
    print("=" * 60)
    
    # 환경 변수 확인
    from app.core.config import env_config
    
    print("\n📋 환경 설정 확인:")
    print(f"  - AWS Region: {env_config.aws_region}")
    print(f"  - S3 Bucket: {env_config.s3_bucket_name}")
    print(f"  - AWS Key ID: {'설정됨' if env_config.aws_access_key_id else '미설정'}")
    print(f"  - Supertone API Key: {'설정됨' if env_config.supertone_api_key else '미설정'}")
    
    if not env_config.aws_access_key_id or not env_config.supertone_api_key:
        print("\n⚠️  환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
        sys.exit(1)
    
    # 테스트 실행
    results = []
    
    try:
        results.append(("TTS 테스트", test_tts()))
        results.append(("S3 테스트", test_s3()))
        results.append(("통합 테스트", test_integration()))
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("테스트 결과")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 모든 테스트 통과!")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트 실패")
        sys.exit(1)
