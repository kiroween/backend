# TimeGrave API - Agent Hooks 설정 가이드

이 프로젝트에 추천하는 Agent Hook 설정입니다.

## 설정 방법

1. Command Palette 열기: `Cmd+Shift+P` (Mac) 또는 `Ctrl+Shift+P` (Windows/Linux)
2. "Open Kiro Hook UI" 검색 및 실행
3. 또는 Explorer 뷰에서 "Agent Hooks" 섹션 사용

---

## 추천 Hook 1: Python 파일 린트 체크

**목적**: Python 파일 저장 시 자동으로 코드 스타일 검사 및 수정

### 설정값
- **Hook Name**: `Python Lint Check`
- **Trigger**: `When a user saves a code file`
- **File Pattern**: `**/*.py`
- **Action Type**: `Execute shell command`
- **Command**: 
  ```bash
  ruff check {file_path} --fix
  ```

### 효과
- 코드 저장 시 자동으로 ruff가 실행되어 스타일 문제를 감지하고 자동 수정
- PEP 8 준수 및 일관된 코드 스타일 유지

---

## 추천 Hook 2: 테스트 파일 자동 실행

**목적**: 테스트 파일 저장 시 해당 테스트만 자동 실행

### 설정값
- **Hook Name**: `Auto Run Tests`
- **Trigger**: `When a user saves a code file`
- **File Pattern**: `tests/test_*.py`
- **Action Type**: `Execute shell command`
- **Command**: 
  ```bash
  pytest {file_path} -v --tb=short
  ```

### 효과
- 테스트 파일 수정 후 저장하면 즉시 해당 테스트 실행
- 빠른 피드백으로 TDD 워크플로우 개선

---

## 추천 Hook 3: 라우터 변경 시 테스트 확인

**목적**: API 라우터 파일 변경 시 관련 테스트 업데이트 필요 여부 확인

### 설정값
- **Hook Name**: `Router Change Review`
- **Trigger**: `When a user saves a code file`
- **File Pattern**: `app/routers/*.py`
- **Action Type**: `Send message to agent`
- **Message**: 
  ```
  라우터 파일 {file_path}가 변경되었습니다. 
  다음을 확인해주세요:
  1. 관련 테스트 파일이 업데이트되어야 하는지
  2. API 스키마 변경사항이 있는지
  3. 문서 업데이트가 필요한지
  ```

### 효과
- API 엔드포인트 변경 시 테스트 누락 방지
- 일관된 API 개발 프로세스 유지

---

## 추천 Hook 4: 모델 변경 시 마이그레이션 체크

**목적**: 데이터베이스 모델 변경 시 마이그레이션 필요 여부 확인

### 설정값
- **Hook Name**: `Model Change Check`
- **Trigger**: `When a user saves a code file`
- **File Pattern**: `app/models/*.py`
- **Action Type**: `Send message to agent`
- **Message**: 
  ```
  데이터베이스 모델 {file_path}가 변경되었습니다.
  스키마 변경사항을 확인하고 필요한 경우 마이그레이션 스크립트를 제안해주세요.
  ```

### 효과
- 데이터베이스 스키마 변경 시 마이그레이션 누락 방지
- 데이터 무결성 유지

---

## 추천 Hook 5: 전체 테스트 실행 (수동)

**목적**: 버튼 클릭으로 전체 테스트 스위트 실행

### 설정값
- **Hook Name**: `Run All Tests`
- **Trigger**: `Manual (button click)`
- **Action Type**: `Execute shell command`
- **Command**: 
  ```bash
  pytest tests/ -v --tb=short
  ```

### 효과
- 커밋 전 전체 테스트를 쉽게 실행
- CI/CD 전에 로컬에서 빠른 검증

---

## 추천 Hook 6: Dockerfile 변경 시 빌드 테스트

**목적**: Dockerfile 수정 시 Docker 이미지 빌드 가능 여부 확인

### 설정값
- **Hook Name**: `Docker Build Test`
- **Trigger**: `When a user saves a code file`
- **File Pattern**: `Dockerfile`
- **Action Type**: `Execute shell command`
- **Command**: 
  ```bash
  docker build -t timegrave-api:test . --no-cache
  ```

### 효과
- Dockerfile 변경 시 즉시 빌드 오류 감지
- AWS ECS/ECR 배포 전 로컬 검증

---

## 추천 Hook 7: 배포 전 체크리스트 (수동)

**목적**: AWS 배포 전 필수 검증 항목 확인

### 설정값
- **Hook Name**: `Pre-Deploy Checklist`
- **Trigger**: `Manual (button click)`
- **Action Type**: `Send message to agent`
- **Message**: 
  ```
  AWS 배포 전 체크리스트를 확인해주세요:
  
  1. 모든 테스트 통과 확인 (pytest tests/ -v)
  2. Docker 이미지 빌드 성공 확인
  3. 환경변수 설정 확인 (.env 파일)
  4. 데이터베이스 마이그레이션 필요 여부
  5. API 엔드포인트 변경사항 문서화
  6. 보안 설정 확인 (CORS, 인증 등)
  7. 로그 레벨 설정 (프로덕션: INFO 이상)
  
  각 항목을 검토하고 문제가 있으면 알려주세요.
  ```

### 효과
- 배포 전 누락 항목 방지
- 일관된 배포 프로세스 유지

---

## 추천 Hook 8: Docker Compose 검증

**목적**: docker-compose.yml 변경 시 설정 유효성 검사

### 설정값
- **Hook Name**: `Docker Compose Validate`
- **Trigger**: `When a user saves a code file`
- **File Pattern**: `docker-compose.yml`
- **Action Type**: `Execute shell command`
- **Command**: 
  ```bash
  docker-compose config
  ```

### 효과
- docker-compose 설정 오류 즉시 감지
- 로컬 개발 환경 안정성 향상

---

## 추천 Hook 9: AWS 배포 스크립트 생성 (수동)

**목적**: AWS ECS/ECR 배포를 위한 스크립트 및 설정 생성 지원

### 설정값
- **Hook Name**: `Generate AWS Deploy Config`
- **Trigger**: `Manual (button click)`
- **Action Type**: `Send message to agent`
- **Message**: 
  ```
  이 FastAPI 프로젝트를 AWS에 배포하기 위한 설정을 생성해주세요:
  
  1. ECR에 Docker 이미지 푸시 스크립트
  2. ECS Task Definition (Fargate)
  3. 필요한 환경변수 목록
  4. RDS 연결 설정 (SQLite → PostgreSQL 마이그레이션 고려)
  5. Application Load Balancer 설정 가이드
  6. CloudWatch 로깅 설정
  
  현재 프로젝트 구조를 분석하여 최적의 배포 설정을 제안해주세요.
  ```

### 효과
- AWS 배포 설정을 빠르게 생성
- 베스트 프랙티스 기반 인프라 구성

---

## 추천 Hook 10: 프로덕션 환경 체크

**목적**: 프로덕션 배포 시 보안 및 성능 설정 확인

### 설정값
- **Hook Name**: `Production Readiness Check`
- **Trigger**: `Manual (button click)`
- **Action Type**: `Send message to agent`
- **Message**: 
  ```
  프로덕션 배포 준비 상태를 점검해주세요:
  
  **보안**
  - DEBUG 모드 비활성화 확인
  - CORS 설정이 특정 도메인으로 제한되어 있는지
  - 비밀키 및 환경변수가 하드코딩되지 않았는지
  - SQL Injection 방어 확인
  
  **성능**
  - 데이터베이스 연결 풀 설정
  - 적절한 타임아웃 설정
  - 로깅 레벨 최적화
  
  **인프라**
  - Health check 엔드포인트 동작 확인
  - 컨테이너 리소스 제한 설정
  - 자동 재시작 정책
  
  각 항목을 검토하고 개선사항을 제안해주세요.
  ```

### 효과
- 프로덕션 배포 전 보안 취약점 사전 차단
- 성능 최적화 기회 발견

---

## AWS 배포 워크플로우 예시

```bash
# 1. 로컬 테스트
Hook: "Run All Tests" 실행

# 2. Docker 빌드 테스트
Hook: "Docker Build Test" 자동 실행 (Dockerfile 저장 시)

# 3. 배포 전 체크리스트
Hook: "Pre-Deploy Checklist" 실행

# 4. 프로덕션 준비 확인
Hook: "Production Readiness Check" 실행

# 5. AWS 배포 (수동 또는 CI/CD)
docker build -t timegrave-api:latest .
docker tag timegrave-api:latest [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/timegrave-api:latest
docker push [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/timegrave-api:latest
aws ecs update-service --cluster timegrave-cluster --service timegrave-service --force-new-deployment
```

---

## 사용 팁

### 개발 단계별 추천 Hook

**일상 개발 (항상 활성화)**
1. ✅ **Python Lint Check** - 코드 품질 유지에 가장 효과적
2. ✅ **Auto Run Tests** - 테스트가 빠른 경우 권장
3. ✅ **Docker Compose Validate** - 로컬 환경 안정성

**API 개발 시**
4. ✅ **Router Change Review** - API 변경 추적
5. ✅ **Model Change Check** - 스키마 변경 관리

**배포 준비 시 (수동 실행)**
6. 🔘 **Run All Tests** - 전체 테스트 실행
7. 🔘 **Pre-Deploy Checklist** - 배포 전 체크리스트
8. 🔘 **Production Readiness Check** - 프로덕션 준비 확인

**AWS 배포 설정 시**
9. 🔘 **Generate AWS Deploy Config** - 배포 설정 생성
10. ✅ **Docker Build Test** - Dockerfile 변경 시 자동 검증

### 주의사항

- **Docker Build Test**: 빌드 시간이 길 수 있으므로 필요시에만 활성화
- **테스트 Hook**: 테스트가 느리면 수동 실행 권장
- **AI 메시지 Hook**: 복잡한 검증이 필요한 경우에 유용
- **파일 패턴**: 필요에 따라 더 구체적으로 조정 가능

## 다음 단계

1. Kiro Hook UI 열기
2. 위 설정 중 필요한 Hook 생성
3. 실제 파일 저장하며 동작 확인
4. 필요에 따라 커스터마이징

---

**참고**: Hook은 언제든지 비활성화하거나 수정할 수 있습니다.
