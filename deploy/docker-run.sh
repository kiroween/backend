#!/bin/bash
# Docker 컨테이너 실행 스크립트
# ⚠️ 실행 위치: EC2 인스턴스 내부
#
# 사용법:
#   cd ~/timegrave-api/deploy
#   ./docker-run.sh

set -e

echo "🔍 현재 위치: $(pwd)"
echo "🔍 스크립트 위치: $0"

# 스크립트가 있는 디렉토리 (deploy/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📂 스크립트 디렉토리: $SCRIPT_DIR"

# 프로젝트 루트 (deploy의 상위)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
echo "📂 프로젝트 루트: $PROJECT_ROOT"

# 환경변수 파일 확인
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "❌ .env 파일이 없습니다: $SCRIPT_DIR/.env"
    exit 1
fi
echo "✅ .env 파일 확인: $SCRIPT_DIR/.env"

# 프로젝트 루트로 이동
cd "$PROJECT_ROOT"
echo "📂 이동 후 위치: $(pwd)"

# 필수 파일 확인
echo ""
echo "🔍 필수 파일 확인..."
for file in pyproject.toml Dockerfile.prod README.md; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 없음"
        exit 1
    fi
done

if [ -d "app" ]; then
    echo "  ✅ app/"
else
    echo "  ❌ app/ 없음"
    exit 1
fi

echo "✅ 모든 필수 파일 확인 완료"
echo ""

# 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 중지 및 제거..."
sudo docker stop timegrave-api 2>/dev/null || true
sudo docker rm timegrave-api 2>/dev/null || true

# 이미지 빌드
echo "🔨 Docker 이미지 빌드..."
echo "   빌드 컨텍스트: $(pwd)"
echo "   Dockerfile: Dockerfile.prod"
sudo docker build -f Dockerfile.prod -t timegrave-api:latest .

# 컨테이너 실행
echo ""
echo "🚀 컨테이너 실행..."
sudo docker run -d \
    --name timegrave-api \
    --restart unless-stopped \
    -p 80:8000 \
    --env-file "$SCRIPT_DIR/.env" \
    -e TZ=Asia/Seoul \
    -v "$PROJECT_ROOT/data:/app/data" \
    -v /etc/localtime:/etc/localtime:ro \
    -v /etc/timezone:/etc/timezone:ro \
    timegrave-api:latest

echo "✅ 컨테이너 실행 완료!"
echo "📊 컨테이너 상태 확인: sudo docker ps"
echo "📝 로그 확인: sudo docker logs -f timegrave-api"
