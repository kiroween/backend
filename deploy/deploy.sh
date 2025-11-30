#!/bin/bash
# 자동 배포 스크립트
# ⚠️ 실행 위치: 로컬 컴퓨터
#
# 사용법:
#   1. deploy/.env.deploy 파일 생성 및 설정
#   2. ./deploy.sh 실행

set -e

# .env.deploy 파일 로드
if [ -f .env.deploy ]; then
    echo "📄 .env.deploy 파일 로드 중..."
    export $(grep -v '^#' .env.deploy | xargs)
else
    echo "❌ .env.deploy 파일이 없습니다."
    echo "   .env.deploy.example을 참고하여 생성하세요."
    exit 1
fi

# 필수 환경변수 확인
if [ -z "$EC2_HOST" ] || [ -z "$EC2_KEY" ]; then
    echo "❌ 필수 환경변수가 설정되지 않았습니다."
    echo "   EC2_HOST와 EC2_KEY를 .env.deploy에 설정하세요."
    exit 1
fi

# 기본값 설정
EC2_USER="${EC2_USER:-ubuntu}"
REPO_URL="${REPO_URL:-https://github.com/kiroween/backend.git}"
BRANCH="${BRANCH:-main}"

echo "🚀 TimeGrave API 배포 시작..."
echo "📍 대상 서버: $EC2_USER@$EC2_HOST"

# SSH 연결 테스트
echo "🔌 SSH 연결 테스트..."
ssh -i "$EC2_KEY" -o ConnectTimeout=10 "$EC2_USER@$EC2_HOST" "echo '✅ SSH 연결 성공'"

# 배포 실행
echo "📦 배포 실행..."
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" bash -s << EOF
set -e

REPO_URL="$REPO_URL"
BRANCH="$BRANCH"

cd ~/timegrave-api 2>/dev/null || cd ~

# Git 저장소 업데이트 또는 클론
if [ -d "timegrave-api/.git" ]; then
    echo "📥 코드 업데이트..."
    cd timegrave-api
    git fetch origin
    git reset --hard origin/\$BRANCH
    git pull origin \$BRANCH
elif [ -d ".git" ]; then
    echo "📥 코드 업데이트..."
    git fetch origin
    git reset --hard origin/\$BRANCH
    git pull origin \$BRANCH
else
    echo "📥 저장소 클론..."
    cd ~
    git clone \$REPO_URL timegrave-api
    cd timegrave-api
fi

# 환경변수 파일 확인
if [ ! -f "deploy/.env" ]; then
    echo "⚠️  .env 파일이 없습니다. 수동으로 생성해주세요."
    exit 1
fi

# Docker 컨테이너 재시작
echo "🔄 컨테이너 재시작..."
cd deploy
bash docker-run.sh

# 헬스체크
echo "🏥 헬스체크..."
sleep 5
curl -f http://localhost/ || echo "⚠️  헬스체크 실패"

echo "✅ 배포 완료!"
EOF

echo "🎉 배포가 완료되었습니다!"
echo "🌐 API 접속: http://$EC2_HOST"
