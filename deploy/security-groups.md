# AWS 보안 그룹 설정 가이드

## EC2 인스턴스 보안 그룹

### 인바운드 규칙

| 유형 | 프로토콜 | 포트 범위 | 소스 | 설명 |
|------|----------|-----------|------|------|
| SSH | TCP | 22 | 내 IP 또는 특정 IP | SSH 접속 (관리용) |
| HTTP | TCP | 80 | 0.0.0.0/0 | 웹 트래픽 |
| HTTPS | TCP | 443 | 0.0.0.0/0 | 보안 웹 트래픽 |
| Custom TCP | TCP | 8000 | 내 IP | 개발/디버깅용 (선택사항) |

### 아웃바운드 규칙

| 유형 | 프로토콜 | 포트 범위 | 대상 | 설명 |
|------|----------|-----------|------|------|
| All traffic | All | All | 0.0.0.0/0 | 모든 아웃바운드 허용 |

### AWS CLI로 생성하기

```bash
# 보안 그룹 생성
aws ec2 create-security-group \
    --group-name timegrave-api-sg \
    --description "Security group for TimeGrave API" \
    --vpc-id vpc-xxxxxxxx

# SSH 규칙 추가 (내 IP만 허용)
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 22 \
    --cidr $(curl -s https://checkip.amazonaws.com)/32

# HTTP 규칙 추가
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# HTTPS 규칙 추가
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

## RDS 보안 그룹

### 인바운드 규칙

| 유형 | 프로토콜 | 포트 범위 | 소스 | 설명 |
|------|----------|-----------|------|------|
| PostgreSQL | TCP | 5432 | EC2 보안 그룹 ID | EC2에서만 접근 허용 |
| PostgreSQL | TCP | 5432 | 내 IP | 관리/디버깅용 (선택사항) |

### 아웃바운드 규칙

기본 설정 유지 (모든 트래픽 허용)

### AWS CLI로 생성하기

```bash
# RDS 보안 그룹 생성
aws ec2 create-security-group \
    --group-name timegrave-rds-sg \
    --description "Security group for TimeGrave RDS" \
    --vpc-id vpc-xxxxxxxx

# EC2 보안 그룹에서 PostgreSQL 접근 허용
aws ec2 authorize-security-group-ingress \
    --group-id sg-rds-xxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --source-group sg-ec2-xxxxxxxx

# 내 IP에서 PostgreSQL 접근 허용 (선택사항)
aws ec2 authorize-security-group-ingress \
    --group-id sg-rds-xxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --cidr $(curl -s https://checkip.amazonaws.com)/32
```

## 보안 모범 사례

### 1. SSH 접근 제한
- 특정 IP 주소만 허용
- 키 기반 인증만 사용 (비밀번호 인증 비활성화)
- 필요시 Bastion Host 사용

### 2. 최소 권한 원칙
- 필요한 포트만 열기
- 소스를 가능한 한 제한적으로 설정
- 개발용 포트는 프로덕션에서 제거

### 3. RDS 보안
- 퍼블릭 액세스 비활성화 (VPC 내부에서만 접근)
- EC2 보안 그룹만 허용
- SSL/TLS 연결 강제

### 4. 정기적인 검토
- 사용하지 않는 규칙 제거
- 보안 그룹 감사 로그 확인
- AWS Security Hub 활용

## HTTPS 설정 (선택사항)

### Let's Encrypt + Nginx 리버스 프록시

```bash
# Nginx 설치
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Nginx 설정
sudo nano /etc/nginx/sites-available/timegrave
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/timegrave /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com
```

## 모니터링

### CloudWatch 알람 설정
- 비정상적인 트래픽 패턴 감지
- 실패한 SSH 로그인 시도 모니터링
- 보안 그룹 변경 알림

### VPC Flow Logs
- 네트워크 트래픽 분석
- 보안 위협 탐지
- 규정 준수 감사
