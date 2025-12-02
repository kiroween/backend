#!/bin/bash

# PostgreSQL 마이그레이션 실행 스크립트
# Usage: ./migrations/run_postgresql_migrations.sh

set -e  # 에러 발생 시 중단

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== PostgreSQL 마이그레이션 시작 ===${NC}\n"

# 환경 변수 확인
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL 환경 변수가 설정되지 않았습니다.${NC}"
    echo "예시: export DATABASE_URL='postgresql://user:password@host:5432/dbname'"
    exit 1
fi

echo -e "${GREEN}✓ DATABASE_URL 확인 완료${NC}"

# 마이그레이션 파일 목록
MIGRATIONS=(
    "add_enroll_share_fields_postgresql.sql"
    "add_invite_token_postgresql.sql"
)

# 각 마이그레이션 실행
for migration in "${MIGRATIONS[@]}"; do
    echo -e "\n${YELLOW}실행 중: $migration${NC}"
    
    if [ ! -f "migrations/$migration" ]; then
        echo -e "${RED}ERROR: migrations/$migration 파일을 찾을 수 없습니다.${NC}"
        exit 1
    fi
    
    # psql로 마이그레이션 실행
    psql "$DATABASE_URL" -f "migrations/$migration"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $migration 완료${NC}"
    else
        echo -e "${RED}✗ $migration 실패${NC}"
        exit 1
    fi
done

echo -e "\n${GREEN}=== 모든 마이그레이션 완료 ===${NC}"

# 테이블 구조 확인
echo -e "\n${YELLOW}=== 테이블 구조 확인 ===${NC}"
psql "$DATABASE_URL" -c "\d tombstones"

echo -e "\n${GREEN}완료!${NC}"
