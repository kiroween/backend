#!/usr/bin/env python3
"""
PostgreSQL 마이그레이션 실행 스크립트
Usage: python migrations/run_postgresql_migrations.py
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql

# 색상 정의
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_colored(message, color=NC):
    """색상이 있는 메시지 출력"""
    print(f"{color}{message}{NC}")


def get_database_url():
    """DATABASE_URL 환경 변수 가져오기"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print_colored("ERROR: DATABASE_URL 환경 변수가 설정되지 않았습니다.", RED)
        print("예시: export DATABASE_URL='postgresql://user:password@host:5432/dbname'")
        sys.exit(1)
    
    return database_url


def run_migration(conn, migration_file):
    """마이그레이션 파일 실행"""
    migration_path = Path(__file__).parent / migration_file
    
    if not migration_path.exists():
        print_colored(f"ERROR: {migration_file} 파일을 찾을 수 없습니다.", RED)
        sys.exit(1)
    
    print_colored(f"\n실행 중: {migration_file}", YELLOW)
    
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_content)
        conn.commit()
        print_colored(f"✓ {migration_file} 완료", GREEN)
        return True
    except Exception as e:
        print_colored(f"✗ {migration_file} 실패: {e}", RED)
        conn.rollback()
        return False


def check_table_structure(conn):
    """테이블 구조 확인"""
    print_colored("\n=== 테이블 구조 확인 ===", YELLOW)
    
    query = """
    SELECT 
        column_name, 
        data_type, 
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_name = 'tombstones'
    ORDER BY ordinal_position;
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
            
            print("\nColumn Name          | Data Type    | Nullable | Default")
            print("-" * 70)
            for col in columns:
                col_name, data_type, nullable, default = col
                default_str = str(default)[:20] if default else 'NULL'
                print(f"{col_name:20} | {data_type:12} | {nullable:8} | {default_str}")
    except Exception as e:
        print_colored(f"테이블 구조 확인 실패: {e}", RED)


def main():
    """메인 함수"""
    print_colored("=== PostgreSQL 마이그레이션 시작 ===\n", YELLOW)
    
    # DATABASE_URL 확인
    database_url = get_database_url()
    print_colored("✓ DATABASE_URL 확인 완료", GREEN)
    
    # 마이그레이션 파일 목록
    migrations = [
        "add_share_token_postgresql.sql",  # 공유 링크 토큰 (기존)
        "add_enroll_share_fields_postgresql.sql",  # 친구 초대 필드
        "add_invite_token_postgresql.sql",  # 초대 링크 토큰
    ]
    
    # 데이터베이스 연결
    try:
        conn = psycopg2.connect(database_url)
        print_colored("✓ 데이터베이스 연결 성공", GREEN)
    except Exception as e:
        print_colored(f"ERROR: 데이터베이스 연결 실패: {e}", RED)
        sys.exit(1)
    
    try:
        # 각 마이그레이션 실행
        for migration in migrations:
            if not run_migration(conn, migration):
                sys.exit(1)
        
        print_colored("\n=== 모든 마이그레이션 완료 ===", GREEN)
        
        # 테이블 구조 확인
        check_table_structure(conn)
        
        print_colored("\n완료!", GREEN)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
