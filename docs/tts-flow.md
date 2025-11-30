# TTS 생성 플로우

## 동작 방식

### 1. 묘비 생성 (POST /api/graves)
```
사용자 → API → DB 저장
- content 저장
- audio_url = NULL
- is_unlocked = false
```
**TTS 생성하지 않음** ✅ 비용 절감

### 2. 잠금 상태 묘비 조회 (GET /api/graves/{id})
```
사용자 → API → DB 조회
응답:
- title만 반환
- content 숨김
- audio_url 숨김
- days_remaining 표시
```
**TTS 생성하지 않음**

### 3. 자동 잠금 해제 (스케줄러)
```
스케줄러 → DB 업데이트
- unlock_date 도달 시
- is_unlocked = true
```

### 4. 잠금 해제된 묘비 조회 (GET /api/graves/{id})

#### 첫 번째 조회 (audio_url이 NULL인 경우)
```
사용자 → API → DB 조회
       ↓
    audio_url이 NULL?
       ↓ YES
    TTS 생성 (content → 음성)
       ↓
    S3 업로드
       ↓
    DB에 audio_url 저장
       ↓
응답:
- content 반환
- audio_url 반환 (새로 생성된 URL)
```

#### 두 번째 이후 조회 (audio_url이 있는 경우)
```
사용자 → API → DB 조회
       ↓
    audio_url이 있음?
       ↓ YES
응답:
- content 반환
- audio_url 반환 (기존 URL 재사용)
```
**TTS 재생성하지 않음** ✅ 비용 절감 & 빠른 응답

## 장점

1. **비용 효율적**: 필요할 때만 TTS 생성
2. **빠른 생성**: 묘비 생성 시 대기 시간 없음
3. **재사용**: 한 번 생성된 음성은 계속 재사용
4. **안정성**: TTS 실패해도 묘비 생성/조회는 정상 동작

## 코드 흐름

```python
# app/services/tombstone_service.py

def get_tombstone(self, tombstone_id: int):
    tombstone = self.repository.get_by_id(tombstone_id)
    
    if tombstone.is_unlocked:
        # 잠금 해제된 경우
        if not tombstone.audio_url:
            # audio_url이 없으면 TTS 생성
            audio_bytes = self.tts_service.generate_audio(tombstone.content)
            audio_url = self.s3_service.upload_audio(audio_bytes, file_name)
            self.repository.update_audio_url(tombstone_id, audio_url)
            return {..., "audio_url": audio_url}
        else:
            # audio_url이 있으면 재사용
            return {..., "audio_url": tombstone.audio_url}
    else:
        # 잠금 상태
        return {..., "days_remaining": days}
```

## 테스트 시나리오

### 시나리오 1: 정상 플로우
1. 묘비 생성 → audio_url = NULL
2. 잠금 상태 조회 → content 숨김
3. 잠금 해제 (스케줄러)
4. 첫 조회 → TTS 생성 → audio_url 저장
5. 두 번째 조회 → audio_url 재사용

### 시나리오 2: TTS 실패
1. 묘비 생성 → audio_url = NULL
2. 잠금 해제
3. 첫 조회 → TTS 생성 실패 → audio_url = NULL
4. content는 정상 반환, audio_url만 NULL

### 시나리오 3: 기존 데이터
1. 이미 잠금 해제된 묘비 (audio_url = NULL)
2. 조회 → TTS 생성 → audio_url 저장
3. 이후 조회 → audio_url 재사용
