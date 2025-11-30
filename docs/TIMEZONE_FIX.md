# 시간대 설정 가이드

## 문제
Docker 컨테이너가 UTC 시간을 사용하여 한국 시간(KST)과 9시간 차이가 발생합니다.
이로 인해 스케줄러가 잘못된 시간에 실행되고, 묘비 잠금 해제가 제대로 작동하지 않습니다.

## 해결 방법

### 1. Dockerfile.prod 수정 (완료)
```dockerfile
# Set timezone to Asia/Seoul (KST)
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

### 2. docker-run.sh 수정 (완료)
```bash
sudo docker run -d \
    --name timegrave-api \
    -e TZ=Asia/Seoul \
    -v /etc/localtime:/etc/localtime:ro \
    -v /etc/timezone:/etc/timezone:ro \
    ...
```

### 3. 배포 후 확인

#### 서버 시간 확인
```bash
# 호스트 서버 시간
date

# Docker 컨테이너 시간
sudo docker exec timegrave-api date
```

두 시간이 동일해야 합니다 (KST).

#### API로 확인
```bash
POST /api/graves/unlock-check
```

응답의 `current_date`가 현재 한국 날짜와 일치해야 합니다.

## 배포 순서

```bash
# 1. 로컬에서 코드 푸시
git add .
git commit -m "Fix timezone to KST"
git push origin main

# 2. 배포 스크립트 실행
cd deploy
./deploy.sh

# 3. 서버에서 시간 확인
ssh -i kiroween.pem ubuntu@your-server
sudo docker exec timegrave-api date

# 4. API 테스트
curl -X POST http://your-server/api/graves/unlock-check \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 트러블슈팅

### 시간이 여전히 UTC인 경우

1. **컨테이너 재빌드**
```bash
cd ~/timegrave-api
sudo docker stop timegrave-api
sudo docker rm timegrave-api
sudo docker rmi timegrave-api:latest
cd deploy
./docker-run.sh
```

2. **환경 변수 확인**
```bash
sudo docker exec timegrave-api env | grep TZ
# 출력: TZ=Asia/Seoul
```

3. **시간대 파일 확인**
```bash
sudo docker exec timegrave-api cat /etc/timezone
# 출력: Asia/Seoul
```

### 스케줄러가 작동하지 않는 경우

1. **로그 확인**
```bash
sudo docker logs -f timegrave-api | grep -i scheduler
```

2. **수동 잠금 해제 테스트**
```bash
POST /api/graves/unlock-check
```

3. **DB 확인**
```bash
sudo docker exec timegrave-api sqlite3 data/timegrave.db \
  "SELECT id, title, unlock_date, is_unlocked FROM tombstones;"
```

## 참고

- 스케줄러는 매일 **00:00 KST**에 자동 실행됩니다
- `unlock_date <= 현재날짜`인 묘비들이 자동으로 잠금 해제됩니다
- 테스트용 `/unlock-check` 엔드포인트로 즉시 확인 가능합니다
