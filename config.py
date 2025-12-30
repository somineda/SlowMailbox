from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgres://user:password@localhost:5432/slowmail"

    # Gmail SMTP 설정
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    DELAY_DAYS: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
