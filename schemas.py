from pydantic import BaseModel, EmailStr
from tortoise.contrib.pydantic import pydantic_model_creator
from models import Letter


class LetterCreate(BaseModel):
    recipient_email: EmailStr
    content: str


LetterResponse = pydantic_model_creator(Letter, name="LetterResponse")
