from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone
from models import Letter
from email_service import send_email

scheduler = AsyncIOScheduler()

#비동기처리
async def check_and_send_letters_async():
    try:
        now = datetime.now(timezone.utc)

        #첫 번째 발송 확인 (7일 후)
        letters_first_send = await Letter.filter(
            sent=False,
            send_at__lte=now
        ).all()

        for letter in letters_first_send:
            #이메일 발송 (첫 번째)
            success = send_email(letter.recipient_email, letter.content, is_second_send=False)

            if success:
                #첫 번째 발송 완료로 표시
                letter.sent = True
                letter.sent_at = datetime.now(timezone.utc)
                await letter.save()
                print(f"[First Send] Letter {letter.id} sent to {letter.recipient_email}")
            else:
                print(f"[First Send] Failed to send letter {letter.id} to {letter.recipient_email}")

        #두 번째 발송 확인 (30일 후)
        letters_second_send = await Letter.filter(
            second_sent=False,
            second_send_at__lte=now
        ).all()

        for letter in letters_second_send:
            #이메일 발송 (두 번째)
            success = send_email(letter.recipient_email, letter.content, is_second_send=True)

            if success:
                #두 번째 발송 완료로 표시
                letter.second_sent = True
                letter.second_sent_at = datetime.now(timezone.utc)
                await letter.save()
                print(f"[Second Send] Letter {letter.id} sent to {letter.recipient_email}")
            else:
                print(f"[Second Send] Failed to send letter {letter.id} to {letter.recipient_email}")

    except Exception as e:
        print(f"Error in check_and_send_letters: {e}")


def start_scheduler():
    scheduler.add_job(
        check_and_send_letters_async,
        'interval',
        minutes=1,
        id='check_letters',
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")
