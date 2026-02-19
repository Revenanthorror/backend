from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, validator
import re
import json
from datetime import datetime

app = FastAPI(title="Сервис сбора обращений абонентов")

class Appeal(BaseModel):
    last_name: str
    first_name: str
    birth_date: date
    phone: str
    email: EmailStr

    @validator('last_name', 'first_name')
    def name_must_be_cyrillic_and_capitalized(cls, v):
        
        if not re.match(r'^[А-ЯЁ][а-яё]*$', v):
            raise ValueError('Должно начинаться с заглавной буквы и содержать только кириллицу')
        return v

    @validator('phone')
    def phone_must_be_valid(cls, v):
        cleaned = re.sub(r'[^\d+]', '', v)

        if not (cleaned.startswith('+7') or cleaned.startswith('8')):
            raise ValueError('Номер телефона должен быть российским (начинаться с +7 или 8)')
        if (cleaned.startswith('+7') and len(cleaned) != 12) or (cleaned.startswith('8') and len(cleaned) != 11):
            raise ValueError('Неверная длина номера телефона')
        
        return v

@app.post("/submit/", summary="Принять обращение абонента")
async def submit_appeal(appeal: Appeal):
    appeal_data = appeal.dict()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"appeal_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(appeal_data, f, ensure_ascii=False, indent=4)
    
    return {
        "status": "success", 
        "message": "Обращение успешно сохранено",
        "filename": filename, 
        "data": appeal_data
    }