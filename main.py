from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone
from typing import List

from database import init_db, close_db
from models import Letter
from schemas import LetterCreate, LetterResponse
from config import settings
import scheduler

app = FastAPI(title="느린 우체통", description="일주일 후에 받는 나에게 보내는 편지")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#애플리케이션 시작 시 db 초기화 
@app.on_event("startup")
async def startup_event():
    await init_db()
    scheduler.start_scheduler()

#스케줄러 종료 및 db 닫기
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown_scheduler()
    await close_db()

#편지 작성
#작성된 편지는 일주일 후랑 한달 후 이메일로 내용 발송
@app.post("/letters/", response_model=LetterResponse)
async def create_letter(letter: LetterCreate):

    now = datetime.now(timezone.utc)

    #발송 시간 계산
    send_at = now + timedelta(minutes=1)
    second_send_at = now + timedelta(minutes=2)

    #새 편지 생성
    db_letter = await Letter.create(
        recipient_email=letter.recipient_email,
        content=letter.content,
        send_at=send_at,
        second_send_at=second_send_at
    )

    return await LetterResponse.from_tortoise_orm(db_letter)

#모든 편지 목록 조회
@app.get("/letters/", response_model=List[LetterResponse])
async def get_letters(skip: int = 0, limit: int = 100):
    queryset = Letter.all().offset(skip).limit(limit)
    return await LetterResponse.from_queryset(queryset)

#특정 편지 조회
@app.get("/letters/{letter_id}", response_model=LetterResponse)
async def get_letter(letter_id: int):
    letter = await Letter.filter(id=letter_id).first()
    if letter is None:
        raise HTTPException(status_code=404, detail="Letter not found")
    return await LetterResponse.from_tortoise_orm(letter)

#메인 페이지 반환
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#테스트용 수동으로 확인
@app.post("/send-pending-emails")
async def send_pending_emails():
    from email_service import send_email

    now = datetime.now(timezone.utc)
    sent_count = 0

    #첫 번째 발송 확인
    letters_first_send = await Letter.filter(
        sent=False,
        send_at__lte=now
    ).all()

    for letter in letters_first_send:
        success = send_email(letter.recipient_email, letter.content, is_second_send=False)
        if success:
            letter.sent = True
            letter.sent_at = datetime.now(timezone.utc)
            await letter.save()
            sent_count += 1
            print(f"[First Send] Letter {letter.id} sent to {letter.recipient_email}")

    #두 번째 발송 확인
    letters_second_send = await Letter.filter(
        second_sent=False,
        second_send_at__lte=now
    ).all()

    for letter in letters_second_send:
        success = send_email(letter.recipient_email, letter.content, is_second_send=True)
        if success:
            letter.second_sent = True
            letter.second_sent_at = datetime.now(timezone.utc)
            await letter.save()
            sent_count += 1
            print(f"[Second Send] Letter {letter.id} sent to {letter.recipient_email}")

    return {
        "message": f"Sent {sent_count} emails",
        "first_send_count": len(letters_first_send),
        "second_send_count": len(letters_second_send)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
