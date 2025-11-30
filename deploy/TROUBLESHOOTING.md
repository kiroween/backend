# 배포 트러블슈팅 가이드

## 1. GitHub 인증 오류

### 오류 메시지:
```
fatal: could not read Username for 'https://github.com': No such device or address
```

### 원인:
Private 저장소를 HTTPS로 클론하려고 할 때 인증 정보가 없어서 발생

### 해결 방법:

#### 방법 1: Public 저장소로 변경 (권장)
GitHub 저장소 설정에서 Public으로 변경

#### 방법 2: SSH 방식 사용 (Private 저장소)

**1) EC2에 SSH 키 생성:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```

**2) GitHub에 SSH 키 등록:**
- GitHub → Settings → SSH and GPG keys → New SSH key
- 위에서 출력된 공개키 붙여넣기

**3) .env.deploy 수정:**
```bash
# HTTPS 대신 SSH 사용
REPO_URL=git@github.com:yourusername/timegrave-api.git
```

#### 방법 3: Personal Access Token 사용

**1) GitHub에서 토큰 생성:**
- GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token → repo 권한 선택

**2) .env.deploy 수정:**
```bash
REPO_URL=https://YOUR_TOKEN@github.com/yourusername/timegrave-api.git
```

⚠️ 보안상 권장하지 않음 (토큰이 노출될 수 있음)

---

## 2. Docker 권한 오류

### 오류 메시지:
```
permission denied while trying to connect to the Docker daemon socket
```

### 원인:
현재 사용자가 Docker 그룹에 속하지 않음

### 해결 방법:

#### 방법 1: sudo 사용 (임시 해결)
스크립트가 이미 `sudo`를 사용하도록 수정되었습니다.

#### 방법 2: Docker 그룹 추가 (영구 해결)

**EC2에서 실행:**
```bash
# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER

# 로그아웃 후 재로그인
exit

# 다시 SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 확인
docker ps  # sudo 없이 실행 가능
```

또는 재로그인 없이:
```bash
newgrp docker
```

---

## 3. 포트 충돌 오류

### 오류 메시지:
```
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```

### 해결 방법:

**1) 80 포트 사용 중인 프로세스 확인:**
```bash
sudo lsof -i :80
```

**2) 다른 포트 사용:**
`docker-run.sh` 수정:
```bash
-p 8080:8000 \  # 80 대신 8080 사용
```

**3) 기존 프로세스 중지:**
```bash
sudo systemctl stop nginx  # Nginx가 실행 중이라면
```

---

## 4. 환경변수 파일 없음

### 오류 메시지:
```
❌ .env 파일이 없습니다.
```

### 해결 방법:

**EC2에서 실행:**
```bash
cd ~/timegrave-api/deploy
cp .env.example .env
nano .env

# 필수 항목 수정:
# - DATABASE_URL
# - JWT_SECRET_KEY
```

---

## 5. 데이터베이스 연결 오류

### PostgreSQL 연결 실패

**1) RDS 보안 그룹 확인:**
- EC2 보안 그룹에서 5432 포트 허용 확인

**2) 연결 문자열 확인:**
```bash
# .env 파일
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/dbname
```

**3) 연결 테스트:**
```bash
sudo docker exec -it timegrave-api python -c "
from app.models.database import engine
with engine.connect() as conn:
    print('✅ 연결 성공')
"
```

---

## 6. 컨테이너가 계속 재시작됨

### 확인 방법:
```bash
sudo docker ps -a
sudo docker logs timegrave-api
```

### 일반적인 원인:

**1) 환경변수 오류:**
- `.env` 파일 확인
- 필수 변수 누락 확인

**2) 데이터베이스 연결 실패:**
- DATABASE_URL 확인
- RDS 보안 그룹 확인

**3) 포트 충돌:**
- 다른 프로세스가 8000 포트 사용 중

---

## 7. 헬스체크 실패

### 오류 메시지:
```
⚠️ 헬스체크 실패
```

### 해결 방법:

**1) 컨테이너 로그 확인:**
```bash
sudo docker logs -f timegrave-api
```

**2) 컨테이너 내부 확인:**
```bash
sudo docker exec -it timegrave-api bash
curl http://localhost:8000/
```

**3) 방화벽 확인:**
```bash
sudo ufw status
sudo ufw allow 80/tcp
```

---

## 8. 빌드 실패

### 오류: pyproject.toml 파일을 찾을 수 없음

**오류 메시지:**
```
COPY failed: file not found in build context or excluded by .dockerignore: stat pyproject.toml: file does not exist
```

**원인:**
잘못된 위치에서 `docker-run.sh`를 실행했거나, Docker 빌드 컨텍스트가 잘못됨

**해결 방법:**

**1) 올바른 위치에서 실행:**
```bash
# ❌ 잘못된 위치
cd ~/timegrave-api
./deploy/docker-run.sh

# ✅ 올바른 위치
cd ~/timegrave-api/deploy
./docker-run.sh
```

**2) 파일 구조 확인:**
```bash
cd ~/timegrave-api
ls -la
# pyproject.toml, Dockerfile.prod, app/ 등이 있어야 함
```

**3) 수동 빌드 테스트:**
```bash
cd ~/timegrave-api
sudo docker build -f Dockerfile.prod -t timegrave-api:test .
```

### 오류: 의존성 설치 실패

**1) Dockerfile.prod 확인:**
```bash
cat Dockerfile.prod
```

**2) 수동 빌드 테스트:**
```bash
cd ~/timegrave-api
sudo docker build -f Dockerfile.prod -t timegrave-api:test .
```

**3) 캐시 없이 빌드:**
```bash
sudo docker build --no-cache -f Dockerfile.prod -t timegrave-api:latest .
```

---

## 유용한 명령어

### Docker 관련
```bash
# 컨테이너 상태 확인
sudo docker ps -a

# 로그 확인
sudo docker logs -f timegrave-api

# 컨테이너 재시작
sudo docker restart timegrave-api

# 컨테이너 중지
sudo docker stop timegrave-api

# 컨테이너 삭제
sudo docker rm timegrave-api

# 이미지 삭제
sudo docker rmi timegrave-api:latest

# 리소스 사용량
sudo docker stats timegrave-api

# 컨테이너 내부 접속
sudo docker exec -it timegrave-api bash
```

### 시스템 관련
```bash
# 디스크 사용량
df -h

# 메모리 사용량
free -h

# 프로세스 확인
ps aux | grep docker

# 포트 확인
sudo netstat -tulpn | grep :80

# 방화벽 상태
sudo ufw status
```

### Git 관련
```bash
# 현재 브랜치 확인
git branch

# 최신 코드 가져오기
git pull origin main

# 변경사항 초기화
git reset --hard origin/main

# 원격 저장소 확인
git remote -v
```

---

## 완전 초기화 (마지막 수단)

모든 것을 처음부터 다시 시작:

```bash
# 1. 컨테이너 및 이미지 삭제
sudo docker stop timegrave-api
sudo docker rm timegrave-api
sudo docker rmi timegrave-api:latest

# 2. 저장소 삭제
cd ~
rm -rf timegrave-api

# 3. 다시 클론
git clone https://github.com/yourusername/timegrave-api.git
cd timegrave-api/deploy

# 4. 환경변수 설정
cp .env.example .env
nano .env

# 5. 배포
./docker-run.sh
```
