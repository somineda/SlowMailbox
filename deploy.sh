#!/bin/bash

# AWS EC2 배포 스크립트

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}느린 우체통 배포 스크립트${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 시스템 업데이트
echo -e "${YELLOW}[1/7] 시스템 업데이트...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# 2. Python 3.11 및 필수 패키지 설치
echo -e "${YELLOW}[2/7] Python 및 필수 패키지 설치...${NC}"
sudo apt-get install -y python3.11 python3.11-venv python3-pip
sudo apt-get install -y nginx postgresql postgresql-contrib

# 3. PostgreSQL 설정
echo -e "${YELLOW}[3/7] PostgreSQL 설정...${NC}"
sudo -u postgres psql << EOF
CREATE DATABASE slowmail;
CREATE USER slowmail WITH PASSWORD 'slowmail123';
GRANT ALL PRIVILEGES ON DATABASE slowmail TO slowmail;
\q
EOF

# 4. 프로젝트 디렉토리 설정
echo -e "${YELLOW}[4/7] 프로젝트 디렉토리 설정...${NC}"
mkdir -p /home/ubuntu/slowmail
cd /home/ubuntu/slowmail

# 5. 가상환경 생성 및 패키지 설치
echo -e "${YELLOW}[5/7] Python 가상환경 및 패키지 설치...${NC}"
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. .env 파일 생성
echo -e "${YELLOW}[6/7] 환경 변수 설정...${NC}"
cat > .env << 'ENVEOF'
DATABASE_URL=postgres://slowmail:slowmail123@localhost:5432/slowmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ENVEOF

echo -e "${YELLOW}⚠️  .env 파일을 수정하세요: nano .env${NC}"

# 7. systemd 서비스 파일 생성
echo -e "${YELLOW}[7/7] systemd 서비스 설정...${NC}"
sudo tee /etc/systemd/system/slowmail.service > /dev/null << EOF
[Unit]
Description=Slow Mailbox FastAPI Application
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/slowmail
Environment="PATH=/home/ubuntu/slowmail/venv/bin"
ExecStart=/home/ubuntu/slowmail/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Nginx 설정
sudo tee /etc/nginx/sites-available/slowmail > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ubuntu/slowmail/static;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/slowmail /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable slowmail
sudo systemctl start slowmail
sudo systemctl restart nginx

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}배포 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo "1. .env 파일 수정: nano /home/ubuntu/slowmail/.env"
echo "2. 서비스 상태 확인: sudo systemctl status slowmail"
echo "3. 로그 확인: sudo journalctl -u slowmail -f"
echo "4. Nginx 상태 확인: sudo systemctl status nginx"
echo ""
echo -e "${YELLOW}서비스 명령어:${NC}"
echo "- 재시작: sudo systemctl restart slowmail"
echo "- 중지: sudo systemctl stop slowmail"
echo "- 시작: sudo systemctl start slowmail"
