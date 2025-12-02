# TimeGrave API

디지털 타임캡슐(묘지) 관리 API - FastAPI 기반

## 프로젝트 개요

TimeGrave는 사용자가 특정 날짜에 열리도록 설정된 디지털 타임캡슐에 기억과 메시지를 저장할 수 있는 웹 애플리케이션입니다.

## 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite / PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Scheduler**: APScheduler
- **Cloud Storage**: AWS S3 (음성 파일 저장)
- **TTS**: Supertone API (텍스트 음성 변환)
- **Package Manager**: uv (Rust 기반 초고속 패키지 관리자)
- **Container**: Docker

## 시작하기

### Docker를 사용한 실행 (권장)

```bash
# Docker 컨테이너 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 로컬 개발 환경 (uv 사용)

#### uv 설치

```bash
# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 또는 pip로 설치
pip install uv
```

#### 프로젝트 실행

```bash
# 가상환경 생성 및 의존성 설치
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
uv pip install -e .

# 개발 의존성 포함 설치
uv pip install -e ".[dev]"

# 개발 서버 실행
uvicorn app.main:app --reload
```

#### uv의 장점

- ⚡ **10-100배 빠른 속도**: Rust로 작성되어 pip보다 훨씬 빠름
- 🔒 **자동 잠금 파일**: 재현 가능한 빌드 보장
- 📦 **통합 도구**: 가상환경, 패키지 설치, 프로젝트 관리 통합

## 주요 기능

- 📝 **타임캡슐 생성**: 미래의 특정 날짜에 열리는 디지털 타임캡슐 생성
- 🔒 **자동 잠금/해제**: 설정된 날짜에 자동으로 잠금 해제
- 🎙️ **TTS 음성 변환**: 잠금 해제된 타임캡슐 조회 시 자동으로 음성 생성
- ☁️ **클라우드 저장**: AWS S3에 음성 파일 안전하게 저장 및 재사용
- 🔐 **사용자 인증**: JWT 기반 인증 시스템
- 🔗 **친구 공유**: 타임캡슐을 친구에게 공유하고 복사할 수 있는 기능

## API 엔드포인트

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 주요 엔드포인트

#### 타임캡슐 관리
- `GET /api/graves` - 모든 타임캡슐 목록 조회
- `POST /api/graves` - 새로운 타임캡슐 생성
- `GET /api/graves/{id}` - 특정 타임캡슐 조회 (잠금 해제 시 TTS 자동 생성 및 음성 URL 제공)

#### 친구 공유 기능
- `POST /api/graves/{id}/share` - 공유 링크 생성
- `GET /api/graves/shared/{share_token}` - 공유된 타임캡슐 조회 (회원가입 필수)
- `POST /api/graves/shared/{share_token}/copy` - 공유된 타임캡슐을 내 계정에 저장

## 환경 설정

### 필수 환경 변수

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
# 데이터베이스
DATABASE_URL=sqlite:///./data/timegrave.db

# JWT 인증
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3 (TTS 음성 파일 저장)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=timegrave-audio

# Supertone TTS API
SUPERTONE_API_KEY=your-supertone-api-key
SUPERTONE_API_URL=https://supertoneapi.com/v1/text-to-speech/a929cf8981cbfd9b8e6eb3
```

자세한 설정 방법은 [TTS 및 S3 연동 가이드](docs/tts-s3-setup.md)를 참고하세요.

## 프로젝트 구조

```
.
├── app/
│   ├── main.py              # FastAPI 애플리케이션 진입점
│   ├── core/                # 설정 및 핵심 기능
│   ├── models/              # SQLAlchemy 데이터베이스 모델
│   ├── schemas/             # Pydantic 스키마
│   ├── repositories/        # 데이터 접근 계층
│   ├── services/            # 비즈니스 로직 (TTS, S3 포함)
│   ├── routers/             # API 라우터
│   └── utils/               # 유틸리티 함수
├── data/                    # SQLite 데이터베이스 파일
├── docs/                    # 문서
├── migrations/              # 데이터베이스 마이그레이션
├── scripts/                 # 유틸리티 스크립트
├── tests/                   # 테스트 코드
├── Dockerfile               # Docker 이미지 정의
├── docker-compose.yml       # Docker Compose 설정
└── pyproject.toml           # 프로젝트 설정 및 의존성
```

## 개발

### 의존성 관리

```bash
# 새 패키지 추가
uv pip install <package-name>

# 개발 의존성 추가
uv pip install --dev <package-name>

# 의존성 업데이트
uv pip install --upgrade <package-name>

# 모든 의존성 동기화
uv pip sync
```

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app

# 특정 테스트 파일 실행
pytest tests/test_tombstone.py

# TTS 및 S3 연동 테스트
python scripts/test_tts_s3.py
```

### 코드 품질

```bash
# Ruff로 린팅
ruff check .

# Ruff로 자동 수정
ruff check --fix .

# 포맷팅
ruff format .
```

## 라이선스

MIT
