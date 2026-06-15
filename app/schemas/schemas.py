import re
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator
from typing import List

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class AppealCreate(BaseModel):
    last_name: str
    first_name: str
    birth_date: date
    phone: str
    email: EmailStr

    @field_validator('last_name', 'first_name')
    @classmethod
    def name_must_be_cyrillic_and_capitalized(cls, v: str) -> str:
        if not re.match(r'^[А-ЯЁ][а-яё]*$', v):
            raise ValueError('Должно начинаться с заглавной буквы и содержать только кириллицу')
        return v

    @field_validator('phone')
    @classmethod
    def phone_must_be_valid(cls, v: str) -> str:
        cleaned = re.sub(r'[^\d+]', '', v)
        if not (cleaned.startswith('+7') or cleaned.startswith('8')):
            raise ValueError('Номер телефона должен быть российским (+7 или 8)')
        if (cleaned.startswith('+7') and len(cleaned) != 12) or (cleaned.startswith('8') and len(cleaned) != 11):
            raise ValueError('Неверная длина номера телефона')
        return v

    @field_validator('birth_date')
    @classmethod
    def birth_date_must_be_in_past(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError('Дата рождения должна быть в прошлом')
        return v

class AppealResponse(BaseModel):
    id: int
    user_id: int | None
    last_name: str
    first_name: str
    birth_date: date
    phone: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class CalculationRequest(BaseModel):
    numbers: List[int]
    delays: List[float]

class IndividualResult(BaseModel):
    number: int
    square: int
    delay: float
    time: float

class CalculationResponse(BaseModel):
    results: List[IndividualResult]
    total_time: float
    parallel_faster_than_sequential: bool
