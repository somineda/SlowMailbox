# 느린 우체통 (Slow Mailbox)

나에게 보내는 편지를 작성하면 일주일 후와 한 달 후, 총 2번 이메일로 받을 수 있는 서비스입니다.

## 기능

### 웹 인터페이스
- 🎨 **아름다운 웹 페이지**: 감성적인 디자인의 편지 작성 폼
- 💫 **별이 반짝이는 배경**: 애니메이션 효과
- 📱 **반응형 디자인**: 모바일, 태블릿, 데스크톱 모두 지원

### 이메일 기능
- 📧 **HTML 이메일**: 예쁘게 꾸며진 이메일 발송
- **7일 후** 첫 번째 리마인더 이메일 발송
- **30일 후** 두 번째 리마인더 이메일 발송
- 각 이메일에 **PNG 이미지를 랜덤으로 첨부**
- "새해 다짐 잊지 않으셨죠?"라는 메시지와 함께 편지 내용 수신

### API
- 편지 생성, 조회 REST API 제공

## 기술 스택

- FastAPI (비동기 웹 프레임워크)
- PostgreSQL
- TortoiseORM (비동기 ORM)
- Jinja2 (템플릿 엔진)
- APScheduler
- Gmail SMTP
- HTML/CSS/JavaScript (프론트엔드)

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

## 사용 방법

### 웹 인터페이스로 편지 작성

1. 브라우저에서 `http://localhost:8000` 접속
2. 아름다운 웹 페이지에서 이메일 주소와 편지 내용 입력
3. "편지 보내기" 버튼 클릭
4. 성공 메시지 확인
5. 7일 후와 30일 후에 이메일 확인!

### API로 편지 작성

직접 API를 호출할 수도 있습니다:

```bash
curl -X POST "http://localhost:8000/letters/" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "your_email@gmail.com",
    "content": "2025년 새해 다짐: 매일 운동하기!"
  }'
```

## 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_api.py

# 커버리지 리포트 포함
pytest --cov=. --cov-report=html

# 상세한 출력
pytest -v
```

### 테스트 구조

```
tests/
├── conftest.py              # 테스트 설정 및 fixture
├── test_api.py              # API 엔드포인트 테스트
├── test_email_service.py    # 이메일 서비스 테스트
└── test_scheduler.py        # 스케줄러 로직 테스트
```

### 테스트 커버리지

테스트는 다음을 검증합니다:
- ✅ 편지 생성 API (7일/30일 발송 시간 설정)
- ✅ 편지 조회 API (전체/개별/페이지네이션)
- ✅ 이메일 발송 기능 (첫 번째/두 번째 발송)
- ✅ PNG 이미지 랜덤 선택 및 첨부
- ✅ 스케줄러 로직 (발송 시간 체크, 상태 업데이트)
- ✅ 에러 핸들링 및 예외 처리

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
├── email_service.py     # HTML 이메일 전송 + PNG 랜덤 첨부
├── scheduler.py         # 백그라운드 스케줄러
├── requirements.txt     # 필요 패키지
├── pytest.ini           # pytest 설정
├── .env.example         # 환경 변수 예시
├── .gitignore           # Git 제외 파일
├── templates/           # Jinja2 템플릿
│   ├── index.html       # 메인 웹 페이지
│   └── email_template.html  # HTML 이메일 템플릿
├── static/              # 정적 파일
│   ├── css/
│   │   └── style.css    # 웹페이지 스타일
│   └── js/
│       └── main.js      # 폼 제출 로직
├── png/                 # 이메일에 첨부할 PNG 이미지 폴더
│   ├── image1.png
│   └── image2.png
├── tests/               # 테스트 파일
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_email_service.py
│   └── test_scheduler.py
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

## 무료 배포 (Render)

### 1. GitHub에 코드 푸시

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/slowmail.git
git push -u origin main
```

### 2. Render 배포

1. [Render](https://render.com) 가입 (GitHub 계정으로 로그인)
2. Dashboard → "New" → "Web Service" 클릭
3. GitHub 저장소 연결
4. 다음 설정 입력:
   - **Name**: slowmail
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. "Create Web Service" 클릭

### 3. PostgreSQL 추가

1. Dashboard → "New" → "PostgreSQL" 클릭
2. Name: slowmail-db
3. Plan: Free
4. "Create Database" 클릭

### 4. 환경 변수 설정

Web Service → Environment 탭에서 추가:

- `DATABASE_URL`: PostgreSQL의 Internal Database URL 복사해서 붙여넣기
- `SMTP_SERVER`: smtp.gmail.com
- `SMTP_PORT`: 587
- `SMTP_USERNAME`: Gmail 주소
- `SMTP_PASSWORD`: Gmail 앱 비밀번호

### 5. 배포 완료!

- 자동으로 빌드 시작
- 5-10분 후 배포 완료
- 할당된 URL로 접속 가능 (예: https://slowmail.onrender.com)

**주의**: Render 무료 플랜은 15분간 요청이 없으면 슬립 모드로 전환됩니다. 첫 접속 시 약간 느릴 수 있습니다.

## 라이선스

MIT
