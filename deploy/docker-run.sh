#!/bin/bash
# Docker 컨테이너 실행 스크립트
# ⚠️ 실행 위치: EC2 인스턴스 내부
#
# 사용법:
#   cd ~/timegrave-api/deploy
#   ./docker-run.sh

set -e

# 환경변수 파일 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다. .env.example을 참고하여 생성하세요."
    exit 1
fi

# 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 중지 및 제거..."
docker stop timegrave-api 2>/dev/null || true
docker rm timegrave-api 2>/dev/null || true

# 이미지 빌드
echo "🔨 Docker 이미지 빌드..."
docker build -f Dockerfile.prod -t timegrave-api:latest .

# 컨테이너 실행
echo "🚀 컨테이너 실행..."
docker run -d \
    --name timegrave-api \
    --restart unless-stopped \
    -p 80:8000 \
    --env-file .env \
    -v $(pwd)/data:/app/data \
    timegrave-api:latest

echo "✅ 컨테이너 실행 완료!"
echo "📊 컨테이너 상태 확인: docker ps"
echo "📝 로그 확인: docker logs -f timegrave-api"
