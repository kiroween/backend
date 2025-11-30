#!/bin/bash
# 로컬에서 Docker 빌드 테스트
# ⚠️ 실행 위치: 로컬 또는 EC2 (프로젝트 루트에서)

set -e

echo "🧪 Docker 빌드 테스트..."

# 현재 위치 확인
if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml이 없습니다."
    echo "현재 위치: $(pwd)"
    echo ""
    echo "올바른 사용법:"
    echo "  cd ~/timegrave-api"
    echo "  bash deploy/test-build.sh"
    exit 1
fi

echo "✅ 현재 위치: $(pwd)"
echo ""
echo "📂 필수 파일 확인:"
echo "  - pyproject.toml: $([ -f pyproject.toml ] && echo '✅' || echo '❌')"
echo "  - Dockerfile.prod: $([ -f Dockerfile.prod ] && echo '✅' || echo '❌')"
echo "  - README.md: $([ -f README.md ] && echo '✅' || echo '❌')"
echo "  - app/: $([ -d app ] && echo '✅' || echo '❌')"
echo ""

# Docker 빌드 테스트
echo "🔨 Docker 이미지 빌드 시작..."
docker build -f Dockerfile.prod -t timegrave-api:test .

echo ""
echo "✅ 빌드 성공!"
echo "🧹 테스트 이미지 삭제..."
docker rmi timegrave-api:test

echo ""
echo "🎉 모든 테스트 통과!"
