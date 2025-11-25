# TimeGrave API

디지털 타임캡슐(묘지) 관리 API - FastAPI 기반

## 프로젝트 개요

TimeGrave는 사용자가 특정 날짜에 열리도록 설정된 디지털 타임캡슐에 기억과 메시지를 저장할 수 있는 웹 애플리케이션입니다.

## 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Scheduler**: APScheduler
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

### 로컬 개발 환경

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload
```

## API 엔드포인트

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 주요 엔드포인트

- `GET /api/graveyard` - 모든 타임캡슐 목록 조회
- `POST /api/tombstones` - 새로운 타임캡슐 생성
- `GET /api/tombstones/{id}` - 특정 타임캡슐 조회

## 프로젝트 구조

```
.
├── app/
│   ├── main.py              # FastAPI 애플리케이션 진입점
│   ├── models/              # SQLAlchemy 데이터베이스 모델
│   ├── schemas/             # Pydantic 스키마
│   ├── repositories/        # 데이터 접근 계층
│   ├── services/            # 비즈니스 로직
│   └── routers/             # API 라우터
├── data/                    # SQLite 데이터베이스 파일
├── tests/                   # 테스트 코드
├── Dockerfile               # Docker 이미지 정의
├── docker-compose.yml       # Docker Compose 설정
└── requirements.txt         # Python 의존성
```

## 개발

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app

# 특정 테스트 파일 실행
pytest tests/test_tombstone.py
```

## 라이선스

MIT
