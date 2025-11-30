#!/bin/bash
# EC2 인스턴스 초기 설정 스크립트
# ⚠️ 실행 위치: EC2 인스턴스 내부
# Ubuntu 22.04 LTS 기준
#
# 사용법:
#   1. 로컬에서 EC2에 SSH 접속: ssh -i key.pem ubuntu@ec2-ip
#   2. EC2에서 이 스크립트 실행: ./ec2-setup.sh

set -e

echo "🚀 EC2 인스턴스 초기 설정 시작..."

# 시스템 업데이트
echo "📦 시스템 패키지 업데이트..."
sudo apt-get update
sudo apt-get upgrade -y

# Docker 설치
echo "🐳 Docker 설치..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker 권한 설정
sudo usermod -aG docker $USER

# Docker 서비스 시작 및 활성화
sudo systemctl start docker
sudo systemctl enable docker

# Git 설치
echo "📚 Git 설치..."
sudo apt-get install -y git

# 방화벽 설정 (UFW)
echo "🔒 방화벽 설정..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 애플리케이션 디렉토리 생성
echo "📁 애플리케이션 디렉토리 생성..."
mkdir -p ~/timegrave-api
mkdir -p ~/timegrave-api/data

echo "✅ EC2 초기 설정 완료!"
echo "⚠️  Docker 권한 적용을 위해 로그아웃 후 다시 로그인하세요."
echo "   또는 다음 명령어를 실행하세요: newgrp docker"
