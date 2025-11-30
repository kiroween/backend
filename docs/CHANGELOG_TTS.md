# TTS 및 S3 연동 변경사항

## 변경 내용

### 제거된 기능
- ❌ `gender` 필드 제거 (성별 구분 기능 삭제)
- ❌ 다중 TTS API URL 제거 (Mok-Sensei, Cindy)

### 단순화된 구조
- ✅ 단일 TTS API URL 사용: `https://supertoneapi.com/v1/text-to-speech/a929cf8981cbfd9b8e6eb3`
- ✅ 환경 변수 단순화: `SUPERTONE_API_URL` 하나만 사용

### TTS 생성 시점 변경
- ✅ **묘비 생성 시**: TTS 생성하지 않음 (비용 절감)
- ✅ **잠금 해제된 묘비 조회 시**: 처음 조회할 때만 TTS 생성 및 S3 업로드
- ✅ **이후 조회**: 저장된 audio_url 재사용 (중복 생성 방지)

## 데이터베이스 변경

```sql
-- 기존 마이그레이션 (gender 필드 제거됨)
ALTER TABLE tombstones ADD COLUMN audio_url VARCHAR(500);
```

## API 변경

### 묘비 생성 요청
```json
{
  "title": "추억의 편지",
  "content": "안녕하세요. 이것은 미래의 나에게 보내는 메시지입니다.",
  "unlock_date": "2025-12-31"
}
```

### 묘비 조회 응답 (잠금 해제 시)
```json
{
  "id": 1,
  "user_id": 1,
  "title": "추억의 편지",
  "content": "안녕하세요. 이것은 미래의 나에게 보내는 메시지입니다.",
  "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1_1733011200.123.mp3",
  "unlock_date": "2025-12-31",
  "is_unlocked": true,
  "created_at": "2024-12-01T00:00:00",
  "updated_at": "2025-12-31T00:00:00"
}
```

## 환경 변수 설정

```bash
# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=kiroween

# Supertone TTS API (단일 URL)
SUPERTONE_API_KEY=your-api-key
SUPERTONE_API_URL=https://supertoneapi.com/v1/text-to-speech/a929cf8981cbfd9b8e6eb3
```

## 테스트

```bash
# TTS 및 S3 연동 테스트
python scripts/test_tts_s3.py
```

## 주요 파일 변경

- `app/core/config.py` - 환경 변수 단순화
- `app/models/tombstone.py` - gender 필드 제거
- `app/schemas/tombstone.py` - gender 필드 제거
- `app/services/tts_service.py` - 단일 API URL 사용
- `app/services/tombstone_service.py` - gender 파라미터 제거
- `app/repositories/tombstone_repository.py` - gender 파라미터 제거
