# TTS 구현 완료 요약

## ✅ 구현 완료

### 핵심 변경사항
**TTS 생성 시점**: 묘비 생성 시 ❌ → 잠금 해제된 묘비 조회 시 ✅

### 동작 방식
1. **묘비 생성**: content만 저장, TTS 생성 안 함
2. **잠금 상태 조회**: content 숨김, TTS 생성 안 함
3. **잠금 해제 후 첫 조회**: TTS 자동 생성 → S3 업로드 → audio_url 저장
4. **이후 조회**: 저장된 audio_url 재사용

## 📁 수정된 파일

### 핵심 로직
- `app/services/tombstone_service.py`
  - `create_tombstone()`: TTS 생성 로직 제거
  - `get_tombstone()`: 잠금 해제 시 TTS 생성 로직 추가

- `app/repositories/tombstone_repository.py`
  - `update_audio_url()`: audio_url 업데이트 메서드 추가

### 설정 파일
- `app/core/config.py`: 단일 API URL 설정
- `app/services/tts_service.py`: gender 파라미터 제거
- `app/services/s3_service.py`: S3 업로드/삭제 기능
- `app/models/tombstone.py`: audio_url 필드만 추가 (gender 제거)
- `app/schemas/tombstone.py`: gender 필드 제거

### 환경 설정
- `.env.example`
- `deploy/.env.example`
- `migrations/add_tts_fields.sql`

### 문서
- `docs/tts-s3-setup.md`: 설정 가이드
- `docs/tts-flow.md`: 동작 플로우 설명
- `README.md`: 기능 설명 업데이트
- `CHANGELOG_TTS.md`: 변경사항 기록

### 테스트
- `scripts/test_tts_s3.py`: TTS/S3 연동 테스트

## 🔧 환경 변수

```bash
# AWS S3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=kiroween

# Supertone TTS API
SUPERTONE_API_KEY=your-api-key
SUPERTONE_API_URL=https://supertoneapi.com/v1/text-to-speech/a929cf8981cbfd9b8e6eb3
```

## 🚀 배포 전 체크리스트

- [ ] 환경 변수 설정 (.env 파일)
- [ ] AWS S3 버킷 생성 및 권한 설정
- [ ] Supertone API 키 발급
- [ ] 데이터베이스 마이그레이션 실행
  ```bash
  sqlite3 data/timegrave.db < migrations/add_tts_fields.sql
  ```
- [ ] 패키지 설치
  ```bash
  pip install boto3 requests
  ```
- [ ] TTS/S3 연동 테스트
  ```bash
  python scripts/test_tts_s3.py
  ```

## 📊 API 응답 예시

### 잠금 해제된 묘비 조회 (첫 조회)
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "title": "추억의 편지",
      "content": "안녕하세요. 미래의 나에게...",
      "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1_1_1733011200.123.mp3",
      "is_unlocked": true
    }
  }
}
```

## 💡 장점

1. **비용 절감**: 필요할 때만 TTS 생성
2. **빠른 응답**: 묘비 생성 시 대기 시간 없음
3. **재사용**: 중복 생성 방지
4. **안정성**: TTS 실패해도 서비스 정상 동작

## 📚 참고 문서

- [TTS 및 S3 설정 가이드](docs/tts-s3-setup.md)
- [TTS 생성 플로우](docs/tts-flow.md)
- [변경사항 로그](CHANGELOG_TTS.md)
