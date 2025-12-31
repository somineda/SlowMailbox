#!/bin/bash

# 배포 수정 스크립트

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}느린 우체통 배포 수정${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. systemd 서비스 파일 수정
echo -e "${YELLOW}[1/5] systemd 서비스 파일 수정...${NC}"
sudo tee /etc/systemd/system/slowmail.service > /dev/null << 'EOF'
[Unit]
Description=Slow Mailbox FastAPI Application
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/SlowMailbox
Environment="PATH=/home/ubuntu/SlowMailbox/venv/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/ubuntu/SlowMailbox/.env
ExecStart=/home/ubuntu/SlowMailbox/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
TimeoutStartSec=300
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ 서비스 파일 수정 완료${NC}"

# 2. Nginx 설정
echo -e "${YELLOW}[2/5] Nginx 설정...${NC}"
sudo tee /etc/nginx/sites-available/slowmail > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /static {
        alias /home/ubuntu/SlowMailbox/static;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/slowmail /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo -e "${GREEN}✓ Nginx 설정 완료${NC}"

# 3. systemd 리로드 및 서비스 재시작
echo -e "${YELLOW}[3/5] 서비스 재시작...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable slowmail
sudo systemctl restart slowmail
sudo systemctl restart nginx

echo -e "${GREEN}✓ 서비스 재시작 완료${NC}"

# 4. 잠시 대기 (서비스가 시작될 시간 주기)
echo -e "${YELLOW}[4/5] 서비스 시작 대기 중... (30초)${NC}"
sleep 30

# 5. 상태 확인
echo -e "${YELLOW}[5/5] 상태 확인...${NC}"
echo ""
echo -e "${GREEN}=== systemd 서비스 상태 ===${NC}"
sudo systemctl status slowmail --no-pager -l

echo ""
echo -e "${GREEN}=== Nginx 상태 ===${NC}"
sudo systemctl status nginx --no-pager

echo ""
echo -e "${GREEN}=== 포트 확인 ===${NC}"
sudo lsof -i :8000 || echo "포트 8000 사용 중인 프로세스 없음"

echo ""
echo -e "${GREEN}=== 최근 로그 ===${NC}"
sudo journalctl -u slowmail -n 50 --no-pager

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}배포 수정 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo "1. 브라우저에서 접속: http://$(curl -s ifconfig.me)"
echo "2. 실시간 로그 확인: sudo journalctl -u slowmail -f"
echo "3. 서비스 재시작: sudo systemctl restart slowmail"
echo ""
