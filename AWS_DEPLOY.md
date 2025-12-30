# AWS EC2 프리티어 배포 가이드

## 🚀 AWS EC2로 무료 배포하기

### 1️⃣ EC2 인스턴스 생성

1. **AWS 콘솔** 접속 → **EC2** 서비스
2. **인스턴스 시작** 클릭
3. 설정:
   - **이름**: slowmail
   - **AMI**: Ubuntu Server 22.04 LTS (프리티어 사용 가능)
   - **인스턴스 유형**: t2.micro (프리티어)
   - **키 페어**: 새로 생성 또는 기존 키 선택 (다운로드 필수!)
   - **네트워크 설정**:
     - SSH (22): 내 IP
     - HTTP (80): 0.0.0.0/0
     - HTTPS (443): 0.0.0.0/0
     - Custom TCP (8000): 0.0.0.0/0
   - **스토리지**: 30GB (프리티어 최대)
4. **인스턴스 시작** 클릭

### 2️⃣ 탄력적 IP 할당 (선택사항, 권장)

1. EC2 콘솔 → **탄력적 IP** → **탄력적 IP 주소 할당**
2. 할당 받은 IP → **연결** → EC2 인스턴스 선택

### 3️⃣ EC2 인스턴스 접속

```bash
# 키 페어 권한 설정 (최초 1회)
chmod 400 your-key.pem

# SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 4️⃣ 프로젝트 업로드

**방법 1: Git 사용 (권장)**
```bash
# EC2 인스턴스에서
cd /home/ubuntu
git clone https://github.com/your-username/slowmail.git
cd slowmail
```

**방법 2: SCP로 파일 전송**
```bash
# 로컬 컴퓨터에서
scp -i your-key.pem -r /Users/yunsomin/Downloads/happynewyear ubuntu@your-ec2-ip:/home/ubuntu/slowmail
```

### 5️⃣ 자동 배포 스크립트 실행

```bash
# EC2 인스턴스에서
cd /home/ubuntu/slowmail
chmod +x deploy.sh
./deploy.sh
```

스크립트가 자동으로 다음을 수행합니다:
- ✅ 시스템 업데이트
- ✅ Python, PostgreSQL, Nginx 설치
- ✅ PostgreSQL 데이터베이스 생성
- ✅ Python 가상환경 설정
- ✅ systemd 서비스 등록
- ✅ Nginx 리버스 프록시 설정

### 6️⃣ 환경 변수 설정

```bash
nano /home/ubuntu/slowmail/.env
```

다음 내용 수정:
```
DATABASE_URL=postgres://slowmail:slowmail123@localhost:5432/slowmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
```

저장: `Ctrl + O` → `Enter` → `Ctrl + X`

### 7️⃣ PNG 이미지 업로드

```bash
# 로컬에서
scp -i your-key.pem /path/to/your/images/*.png ubuntu@your-ec2-ip:/home/ubuntu/slowmail/png/
```

### 8️⃣ 서비스 재시작

```bash
sudo systemctl restart slowmail
```

### 9️⃣ 배포 확인

```bash
# 서비스 상태 확인
sudo systemctl status slowmail

# 로그 확인
sudo journalctl -u slowmail -f

# 브라우저에서 접속
http://your-ec2-public-ip
```

---

## 📋 유용한 명령어

### 서비스 관리
```bash
# 서비스 재시작
sudo systemctl restart slowmail

# 서비스 중지
sudo systemctl stop slowmail

# 서비스 시작
sudo systemctl start slowmail

# 서비스 상태 확인
sudo systemctl status slowmail

# 실시간 로그 확인
sudo journalctl -u slowmail -f

# 최근 100줄 로그
sudo journalctl -u slowmail -n 100
```

### Nginx 관리
```bash
# Nginx 재시작
sudo systemctl restart nginx

# Nginx 설정 테스트
sudo nginx -t

# Nginx 상태 확인
sudo systemctl status nginx
```

### PostgreSQL 관리
```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 확인
\c slowmail
\dt

# 종료
\q
```

### 파일 수정
```bash
# 코드 수정 후
cd /home/ubuntu/slowmail
git pull  # Git 사용 시
sudo systemctl restart slowmail
```

---

## 🔒 보안 설정 (중요!)

### 1. 방화벽 설정 (UFW)
```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### 2. SSL 인증서 설정 (Let's Encrypt - 무료)

도메인이 있다면:

```bash
# Certbot 설치
sudo apt-get install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

### 3. .env 파일 권한 설정
```bash
chmod 600 /home/ubuntu/slowmail/.env
```

---

## 💰 비용 (프리티어)

### 무료 제공
- ✅ EC2 t2.micro: 월 750시간 (1대 24/7 가능)
- ✅ 스토리지: 30GB
- ✅ 데이터 전송: 월 15GB

### 유료 요소
- ⚠️ 탄력적 IP: 사용 중일 때는 무료, 미사용 시 과금
- ⚠️ 데이터 전송: 15GB 초과 시 과금
- ⚠️ 스토리지: 30GB 초과 시 과금

**프리티어 기간**: 가입 후 12개월

---

## 🔧 트러블슈팅

### 서비스가 시작되지 않을 때
```bash
# 상세 로그 확인
sudo journalctl -u slowmail -n 100 --no-pager

# Python 경로 확인
which python3
/home/ubuntu/slowmail/venv/bin/python --version
```

### 데이터베이스 연결 오류
```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h localhost -U slowmail -d slowmail
```

### Nginx 오류
```bash
# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# 설정 테스트
sudo nginx -t
```

### 포트가 이미 사용 중일 때
```bash
# 8000번 포트 사용 프로세스 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 PID
```

---

## 📊 모니터링

### CloudWatch 알람 설정
1. AWS CloudWatch 콘솔
2. **알람 생성**
3. 메트릭: CPU 사용률, 네트워크, 디스크
4. 임계값 설정 및 알림 이메일 추가

### 로그 모니터링
```bash
# 실시간 로그 모니터링
sudo journalctl -u slowmail -f

# 에러만 필터링
sudo journalctl -u slowmail -p err
```

---

## 🎯 배포 완료 체크리스트

- [ ] EC2 인스턴스 생성 및 접속
- [ ] 보안 그룹 설정 (포트 80, 443, 8000 오픈)
- [ ] 프로젝트 코드 업로드
- [ ] deploy.sh 스크립트 실행
- [ ] .env 파일 설정 (Gmail SMTP)
- [ ] PNG 이미지 업로드
- [ ] 서비스 시작 및 상태 확인
- [ ] 브라우저에서 접속 테스트
- [ ] 편지 작성 및 이메일 수신 테스트
- [ ] (선택) 도메인 연결 및 SSL 설정
- [ ] (선택) CloudWatch 알람 설정

---

## 📞 문제 발생 시

1. 서비스 로그 확인: `sudo journalctl -u slowmail -f`
2. Nginx 로그 확인: `sudo tail -f /var/log/nginx/error.log`
3. 데이터베이스 연결 확인: `psql -h localhost -U slowmail -d slowmail`
4. 환경 변수 확인: `cat /home/ubuntu/slowmail/.env`
