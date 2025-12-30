# 느린 우체통 (Slow Mailbox)

나에게 보내는 편지를 작성하면 일주일 후와 한 달 후, 총 2번 이메일로 받을 수 있는 서비스입니다.

## 기능

- 자신의 이메일 주소와 편지 내용을 입력
- **7일 후** 첫 번째 리마인더 이메일 발송
- **30일 후** 두 번째 리마인더 이메일 발송
- 각 이메일에 **png 폴더의 이미지 중 하나를 랜덤으로 첨부**
- "새해 다짐 잊지 않으셨죠?"라는 메시지와 함께 편지 내용 수신
- 모든 편지 관리 및 조회

## 기술 스택

- FastAPI (비동기 웹 프레임워크)
- PostgreSQL
- TortoiseORM (비동기 ORM)
- APScheduler
- Gmail SMTP

## 설치 및 설정

### 1. 필요 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. PostgreSQL 데이터베이스 생성

```bash
# PostgreSQL에 접속
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE slowmail;

# 사용자 생성 (선택사항)
CREATE USER slowmail_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE slowmail TO slowmail_user;
```

### 3. Gmail SMTP 설정

1. Gmail 계정에 로그인
2. Google 계정 설정 > 보안 > 2단계 인증 활성화
3. 앱 비밀번호 생성
   - Google 계정 > 보안 > 앱 비밀번호
   - "메일" 및 "기타" 선택
   - 생성된 16자리 비밀번호를 복사

### 4. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 수정:

```bash
cp .env.example .env
```

`.env` 파일 내용 수정:

```
# TortoiseORM은 postgres:// 프로토콜을 사용합니다 (asyncpg)
DATABASE_URL=postgres://slowmail_user:your_password@localhost:5432/slowmail
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_digit_app_password
```

### 5. PNG 이미지 준비

이메일에 첨부할 PNG 이미지를 `png` 폴더에 추가하세요:

```bash
# png 폴더에 이미지 파일 복사
cp your_images/*.png png/
```

**주의사항:**
- 파일 확장자는 반드시 `.png`여야 합니다
- 최소 1개 이상의 PNG 파일이 있어야 합니다
- 이미지가 없으면 이메일은 전송되지만 이미지는 첨부되지 않습니다
- 이메일 발송 시 랜덤으로 선택됩니다

### 6. 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 사용법

### 편지 작성

```bash
curl -X POST "http://localhost:8000/letters/" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "your_email@gmail.com",
    "content": "2025년에는 매일 운동하기! 건강한 습관 만들기!"
  }'
```

### 모든 편지 조회

```bash
curl "http://localhost:8000/letters/"
```

### 특정 편지 조회

```bash
curl "http://localhost:8000/letters/1"
```

### API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 프로젝트 구조

```
happynewyear/
├── main.py              # FastAPI 애플리케이션 (비동기)
├── models.py            # TortoiseORM 모델
├── schemas.py           # Pydantic 스키마
├── database.py          # TortoiseORM 초기화
├── config.py            # 설정
├── email_service.py     # 이메일 전송 기능 + PNG 랜덤 첨부
├── scheduler.py         # 백그라운드 스케줄러
├── requirements.txt     # 필요 패키지
├── .env.example         # 환경 변수 예시
├── .gitignore           # Git 제외 파일
├── png/                 # 이메일에 첨부할 PNG 이미지 폴더
│   ├── image1.png
│   └── image2.png
└── README.md           # 문서
```

## 동작 원리

1. 사용자가 편지를 작성하면 TortoiseORM을 통해 비동기로 데이터베이스에 저장
2. 발송 시간은 **두 번** 자동 설정:
   - 첫 번째: 현재 시간 + 7일
   - 두 번째: 현재 시간 + 30일
3. 백그라운드 스케줄러가 1분마다 확인
4. 발송 시간이 된 편지를 Gmail SMTP를 통해 발송
   - **PNG 폴더의 이미지 중 하나를 랜덤으로 선택하여 첨부**
   - 첫 번째 발송: "새해 다짐 잊지 않으셨죠?"
   - 두 번째 발송: "새해 다짐 잊지 않으셨죠? (한 달 후 리마인더)"
5. 발송 완료된 편지는 각각 `sent`, `second_sent` 상태로 표시
6. 모든 데이터베이스 작업은 비동기(async/await)로 처리

## 주의사항

- Gmail의 경우 하루 전송 제한이 있습니다 (무료 계정: 500통/일)
- 2단계 인증을 활성화하고 앱 비밀번호를 사용해야 합니다
- `.env` 파일은 절대 git에 커밋하지 마세요
- DATABASE_URL은 `postgres://` 프로토콜을 사용합니다 (TortoiseORM + asyncpg)
- 마이그레이션이 필요한 경우 `aerich`를 사용하세요
- **PNG 이미지**:
  - `png` 폴더에 최소 1개 이상의 PNG 파일이 있어야 합니다
  - 이미지가 없으면 이메일은 전송되지만 이미지는 첨부되지 않습니다
  - 너무 큰 이미지는 이메일 전송 실패 원인이 될 수 있으니 적절한 크기로 준비하세요 (권장: 1MB 이하)

## 라이선스

MIT
# SlowMailbox
