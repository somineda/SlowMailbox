import smtplib
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from jinja2 import Environment, FileSystemLoader
from config import settings

#Jinja2 템플릿 환경 설정
template_env = Environment(loader=FileSystemLoader('templates'))


def get_random_png_image():
    #png 폴더에서 랜덤으로 PNG 이미지를 선택
    png_folder = os.path.join(os.path.dirname(__file__), "png")

    if not os.path.exists(png_folder):
        print(f"PNG folder not found: {png_folder}")
        return None

    png_files = [f for f in os.listdir(png_folder) if f.lower().endswith('.png')]

    if not png_files:
        print("No PNG files found in png folder")
        return None

    selected_file = random.choice(png_files)
    return os.path.join(png_folder, selected_file)


def send_email(to_email: str, letter_content: str, is_second_send: bool = False):
#편지 내용과 이미지가 포함된 HTML 이메일 발송

    #첫 번째 발송과 두 번째 발송에 따라 제목과 본문 변경
    if is_second_send:
        subject = "새해 다짐 잊지 않으셨죠?????"
        time_info = "한 달 전"
    else:
        subject = "새해 다짐 잊지 않으셨죠?"
        time_info = "일주일 전"

    #임베디드 이미지를 위한 related 타입 메시지 생성
    message = MIMEMultipart("related")
    message["Subject"] = subject
    message["From"] = settings.SMTP_USERNAME
    message["To"] = to_email

    #텍스트와 HTML을 위한 alternative 파트 생성
    msg_alternative = MIMEMultipart("alternative")
    message.attach(msg_alternative)

    #플레인 텍스트 버전(임시)
    text_body = f"""
안녕하세요!

{time_info}에 보내신 편지가 도착했습니다.

새해 다짐 잊지 않으셨죠?

===================
{letter_content}
===================

당신의 다짐을 응원합니다!

- 느린 우체통
    """

    #랜덤 이미지 가져오기 
    image_path = get_random_png_image()
    image_cid = "embedded_image"
    has_image = image_path is not None

    #템플릿을 사용한 HTML 버전
    template = template_env.get_template('email_template.html')
    html_body = template.render(
        subject=subject,
        content=letter_content,
        time_info=time_info,
        is_second_send=is_second_send,
        has_image=has_image,
        image_cid=image_cid
    )

    #텍스트와 HTML 파트 첨부
    text_part = MIMEText(text_body, "plain", "utf-8")
    html_part = MIMEText(html_body, "html", "utf-8")
    msg_alternative.attach(text_part)
    msg_alternative.attach(html_part)

    #CID를 사용하여 이미지 임베드
    if has_image:
        try:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                image = MIMEImage(img_data)
                image.add_header('Content-ID', f'<{image_cid}>')
                image.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
                message.attach(image)
                print(f"Embedded image: {os.path.basename(image_path)}")
        except Exception as e:
            print(f"Failed to embed image: {e}")

    #이메일 발송
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
