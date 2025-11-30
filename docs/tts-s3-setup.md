# TTS 및 S3 연동 가이드

## 개요
묘비 타임캡슐이 잠금 해제되어 상세 내용을 조회할 때, content를 TTS로 변환하여 S3에 저장하고 음성 파일 URL을 제공합니다.

## 기능
- 잠금 해제된 묘비를 처음 조회할 때 content를 Supertone TTS API로 음성 변환
- 생성된 음성 파일을 AWS S3에 업로드하고 DB에 저장
- 이후 조회 시에는 저장된 audio_url을 재사용 (중복 생성 방지)
- 묘비가 잠금 상태일 때는 TTS 생성하지 않음

## 설정 방법

### 1. AWS S3 버킷 생성

```bash
# AWS CLI로 S3 버킷 생성
aws s3 mb s3://timegrave-audio --region ap-northeast-2

# 퍼블릭 액세스 설정 (읽기 전용)
aws s3api put-bucket-acl --bucket timegrave-audio --acl public-read
```

### 2. IAM 사용자 생성 및 권한 설정

S3 버킷에 접근할 수 있는 IAM 사용자를 생성하고 다음 권한을 부여합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::timegrave-audio/*"
    }
  ]
}
```

### 3. 환경 변수 설정

`.env` 파일에 다음 설정을 추가합니다:

```bash
# AWS S3 설정
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=timegrave-audio

# Supertone TTS API 설정
SUPERTONE_API_KEY=your-supertone-api-key
SUPERTONE_API_URL=https://supertoneapi.com/v1/text-to-speech/a929cf8981cbfd9b8e6eb3
```

### 4. 패키지 설치

```bash
pip install boto3 requests
```

또는 pyproject.toml이 업데이트되었으므로:

```bash
pip install -e .
```

### 5. 데이터베이스 마이그레이션

기존 데이터베이스에 새로운 컬럼을 추가합니다:

```bash
# SQLite 사용 시
sqlite3 data/timegrave.db < migrations/add_tts_fields.sql

# PostgreSQL 사용 시
psql -h your-rds-endpoint -U username -d timegrave -f migrations/add_tts_fields.sql
```

## API 사용법

### 묘비 생성 (TTS 포함)

```bash
POST /api/graves
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "추억의 편지",
  "content": "안녕하세요. 이것은 미래의 나에게 보내는 메시지입니다.",
  "unlock_date": "2025-12-31"
}
```

**응답:**
```json
{
  "status": 201,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "추억의 편지",
      "unlock_date": "2025-12-31",
      "is_unlocked": false,
      "days_remaining": 365,
      "created_at": "2024-12-01T00:00:00",
      "updated_at": "2024-12-01T00:00:00"
    },
    "response": "기억이 안전하게 봉인되었습니다. 365일 후에 다시 만나요."
  }
}
```

### 묘비 상세 조회 (잠금 해제 시 audio_url 포함)

```bash
GET /api/graves/{grave_id}
Authorization: Bearer <token>
```

**응답 (잠금 해제된 경우):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "추억의 편지",
      "content": "안녕하세요. 이것은 미래의 나에게 보내는 메시지입니다.",
      "audio_url": "https://timegrave-audio.s3.ap-northeast-2.amazonaws.com/tombstone_1_1733011200.123.mp3",
      "unlock_date": "2025-12-31",
      "is_unlocked": true,
      "created_at": "2024-12-01T00:00:00",
      "updated_at": "2025-12-31T00:00:00"
    }
  }
}
```

**응답 (잠금 상태인 경우):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "추억의 편지",
      "unlock_date": "2025-12-31",
      "is_unlocked": false,
      "days_remaining": 365,
      "created_at": "2024-12-01T00:00:00",
      "updated_at": "2024-12-01T00:00:00"
    }
  }
}
```

## 주의사항

1. **TTS 생성 시점**: TTS는 잠금 해제된 묘비를 처음 조회할 때 생성됩니다. 묘비 생성 시에는 생성되지 않습니다.

2. **TTS 실패 시**: TTS 생성이나 S3 업로드가 실패해도 묘비 조회는 정상적으로 진행됩니다. audio_url이 null로 반환됩니다.

3. **비용 관리**: 
   - TTS는 잠금 해제된 묘비를 처음 조회할 때만 생성되므로 비용 효율적입니다
   - 한 번 생성된 음성은 재사용되어 중복 비용이 발생하지 않습니다
   - S3 스토리지와 Supertone API 사용에 따른 비용이 발생할 수 있습니다

4. **보안**: 
   - AWS 자격 증명은 절대 코드에 하드코딩하지 마세요
   - 환경 변수나 AWS Secrets Manager를 사용하세요
   - S3 버킷은 public-read로 설정되어 있으므로 민감한 정보는 저장하지 마세요

5. **파일명 규칙**: `tombstone_{user_id}_{tombstone_id}_{timestamp}.mp3` 형식으로 저장됩니다.

## 트러블슈팅

### S3 업로드 실패
- AWS 자격 증명이 올바른지 확인
- IAM 권한이 올바르게 설정되었는지 확인
- S3 버킷 이름과 리전이 일치하는지 확인

### TTS API 실패
- Supertone API 키가 유효한지 확인
- API URL이 올바른지 확인

### 로그 확인
```bash
# 애플리케이션 로그에서 TTS/S3 관련 메시지 확인
tail -f logs/app.log | grep -E "TTS|S3"
```
