# TimeGrave API - EC2 배포 가이드

EC2에 Docker를 사용하여 TimeGrave API를 배포하는 간단한 가이드입니다.

## 📋 사전 요구사항

- AWS 계정
- EC2 인스턴스 (Ubuntu 22.04 LTS 권장)
- SSH 키 페어
- 도메인 (선택사항)

## 🚀 빠른 시작

### 1. EC2 인스턴스 생성

AWS Console에서:
- AMI: Ubuntu Server 22.04 LTS
- 인스턴스 타입: t2.micro (프리 티어) 또는 t3.small (권장)
- 스토리지: 20GB 이상
- 보안 그룹: `security-groups.md` 참고

### 2. EC2 초기 설정 (⚠️ EC2에서 실행)

```bash
# 로컬에서 SSH로 EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 이제부터는 EC2 내부에서 실행
# 초기 설정 스크립트 다운로드 및 실행
curl -O https://raw.githubusercontent.com/yourusername/timegrave-api/main/deploy/ec2-setup.sh
chmod +x ec2-setup.sh
./ec2-setup.sh

# Docker 권한 적용
newgrp docker
```

### 3. 애플리케이션 배포 (⚠️ EC2에서 실행)

```bash
# EC2에서 계속 진행
# 저장소 클론
cd ~
git clone https://github.com/yourusername/timegrave-api.git
cd timegrave-api

# 환경변수 설정
cd deploy
cp .env.example .env
nano .env  # 환경변수 수정 (DATABASE_URL, JWT_SECRET_KEY 등)

# Docker 컨테이너 실행
# ⚠️ 중요: deploy 폴더에서 실행해야 합니다
chmod +x docker-run.sh
./docker-run.sh
```

**주의사항:**
- `docker-run.sh`는 반드시 `~/timegrave-api/deploy/` 폴더에서 실행해야 합니다
- 스크립트가 자동으로 상위 폴더(프로젝트 루트)에서 Docker 빌드를 수행합니다

### 4. 확인

```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs -f timegrave-api

# API 테스트
curl http://localhost/
```

브라우저에서 `http://your-ec2-ip` 접속하여 확인

## 📁 파일 구조

```
deploy/
├── README.md                # 이 파일
├── ec2-setup.sh            # EC2 초기 설정 스크립트
├── docker-run.sh           # Docker 컨테이너 실행 스크립트
├── deploy.sh               # 자동 배포 스크립트 (로컬에서 실행)
├── .env.example            # 애플리케이션 환경변수 예제 (EC2용)
├── .env.deploy.example     # 배포 스크립트 설정 예제 (로컬용)
├── rds-migration.md        # RDS PostgreSQL 마이그레이션 가이드
└── security-groups.md      # AWS 보안 그룹 설정 가이드
```

## 🔧 환경변수 설정

`.env` 파일에서 다음 항목을 설정하세요:

### 필수 설정

```bash
# 데이터베이스 (SQLite 또는 PostgreSQL)
DATABASE_URL=sqlite:///./data/timegrave.db

# JWT 시크릿 키 (반드시 변경!)
JWT_SECRET_KEY=your-super-secret-key-here
```

### 선택적 설정

```bash
# 애플리케이션 환경
APP_ENV=production
LOG_LEVEL=INFO

# CORS 설정
ALLOWED_ORIGINS=https://yourdomain.com

# 서버 설정
PORT=8000
WORKERS=2
```

## 🗄️ 데이터베이스 옵션

### 옵션 1: SQLite (기본값)
- 간단하고 빠른 시작
- 소규모 트래픽에 적합
- 별도 설정 불필요

```bash
DATABASE_URL=sqlite:///./data/timegrave.db
```

### 옵션 2: PostgreSQL (RDS)
- 프로덕션 환경 권장
- 확장성과 안정성
- 자세한 설정은 `rds-migration.md` 참고

```bash
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/timegrave
```

## 🔄 업데이트 및 재배포

### 방법 1: 수동 업데이트 (⚠️ EC2에서 실행)

```bash
# EC2에 SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# EC2에서 실행
cd ~/timegrave-api
git pull origin main
cd deploy
./docker-run.sh
```

### 방법 2: 자동 배포 (⚠️ 로컬에서 실행)

```bash
# 로컬 컴퓨터에서 실행
cd deploy

# 배포 설정 파일 생성
cp .env.deploy.example .env.deploy
nano .env.deploy  # EC2_HOST, EC2_KEY 등 설정

# 배포 실행 (SSH로 자동 접속하여 배포)
chmod +x deploy.sh
./deploy.sh
```

## 📊 모니터링

### 로그 확인

```bash
# 실시간 로그
docker logs -f timegrave-api

# 최근 100줄
docker logs --tail 100 timegrave-api
```

### 컨테이너 상태

```bash
# 실행 중인 컨테이너
docker ps

# 리소스 사용량
docker stats timegrave-api
```

### 헬스체크

```bash
curl http://localhost/
```

## 🔒 보안 설정

### 1. 보안 그룹 설정
`security-groups.md` 참고

### 2. JWT 시크릿 키 변경
`.env` 파일에서 강력한 시크릿 키 설정:

```bash
# 랜덤 키 생성
openssl rand -hex 32
```

### 3. CORS 설정
프로덕션에서는 특정 도메인만 허용:

```bash
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. HTTPS 설정 (권장)
`security-groups.md`의 HTTPS 섹션 참고

## 🐛 트러블슈팅

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker logs timegrave-api

# 환경변수 확인
docker exec timegrave-api env
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 연결 테스트
docker exec -it timegrave-api python -c "
from app.models.database import engine
with engine.connect() as conn:
    print('연결 성공')
"
```

### 포트 충돌

```bash
# 80 포트 사용 중인 프로세스 확인
sudo lsof -i :80

# 다른 포트로 실행
docker run -p 8080:8000 ...
```

## 💰 비용 최적화

### 프리 티어 활용
- EC2: t2.micro (750시간/월)
- RDS: db.t3.micro (750시간/월)
- 데이터 전송: 15GB/월

### 비용 절감 팁
1. 사용하지 않을 때 인스턴스 중지
2. 예약 인스턴스 고려 (장기 사용시)
3. CloudWatch 알람으로 비정상 트래픽 감지
4. 불필요한 스냅샷 정리

## 📚 추가 리소스

- [RDS PostgreSQL 마이그레이션](rds-migration.md)
- [보안 그룹 설정](security-groups.md)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Docker 공식 문서](https://docs.docker.com/)

## 🆘 지원

문제가 발생하면:
1. 로그 확인: `docker logs timegrave-api`
2. 컨테이너 상태 확인: `docker ps -a`
3. 환경변수 확인: `.env` 파일
4. 보안 그룹 확인: AWS Console

## 📝 체크리스트

배포 전 확인사항:

- [ ] EC2 인스턴스 생성 및 보안 그룹 설정
- [ ] Docker 설치 완료
- [ ] `.env` 파일 생성 및 설정
- [ ] JWT_SECRET_KEY 변경
- [ ] 데이터베이스 연결 설정 (SQLite 또는 RDS)
- [ ] 방화벽 규칙 확인
- [ ] 도메인 연결 (선택사항)
- [ ] HTTPS 설정 (선택사항)
- [ ] 백업 전략 수립
