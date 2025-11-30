# TimeGrave API - 빠른 시작 가이드

## 🚀 uv를 사용한 초고속 설정

### 1. uv 설치

```bash
# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 프로젝트 설정

```bash
# 가상환경 생성 (자동으로 Python 3.11 사용)
uv venv

# 가상환경 활성화
source .venv/bin/activate  # Mac/Linux
# 또는
.venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
# 프로덕션 의존성만 설치
uv pip install -e .

# 개발 의존성 포함 설치 (테스트, 린팅 등)
uv pip install -e ".[dev]"
```

### 4. 서버 실행

```bash
# 개발 서버 실행 (자동 리로드)
uvicorn app.main:app --reload

# 또는 특정 포트로 실행
uvicorn app.main:app --reload --port 8000
```

### 5. API 확인

브라우저에서 다음 URL을 열어보세요:

- **API 문서 (Swagger)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 🐳 Docker로 실행

```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 중지
docker-compose down
```

## 🧪 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일
pytest tests/test_graves.py

# 커버리지 리포트
pytest --cov=app --cov-report=html
```

## 📝 개발 워크플로우

### 새 패키지 추가

```bash
# 프로덕션 의존성 추가
uv pip install <package-name>

# 개발 의존성 추가
uv pip install --dev <package-name>
```

### 코드 품질 체크

```bash
# 린팅
ruff check .

# 자동 수정
ruff check --fix .

# 포맷팅
ruff format .
```

## 💡 유용한 명령어

```bash
# 설치된 패키지 목록
uv pip list

# 패키지 정보 확인
uv pip show <package-name>

# 의존성 트리 확인
uv pip tree

# 캐시 정리
uv cache clean
```

## 🔧 문제 해결

### uv가 설치되지 않는 경우

```bash
# pip로 대체 설치
pip install uv
```

### 가상환경이 활성화되지 않는 경우

```bash
# 수동으로 Python 경로 확인
which python  # Mac/Linux
where python  # Windows

# .venv 폴더 삭제 후 재생성
rm -rf .venv
uv venv
```

### 포트가 이미 사용 중인 경우

```bash
# 다른 포트로 실행
uvicorn app.main:app --reload --port 8001
```

## 📚 다음 단계

1. `.kiro/specs/timegrave-api/tasks.md` 파일을 열어 구현 작업 확인
2. `app/` 디렉토리에서 코드 작성 시작
3. API 엔드포인트 구현 및 테스트

Happy Coding! 🪦✨
