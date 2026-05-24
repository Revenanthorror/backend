from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.models import Appeal
from app.schemas.schemas import AppealCreate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/appeals", tags=["appeals"])

@router.post("/", summary="Сохранить обращение в БД (Требует авторизации эээээ в свагере)")
async def submit_appeal(appeal_data: AppealCreate, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):

    new_appeal = Appeal(**appeal_data.model_dump())
    db.add(new_appeal)
    await db.commit()
    await db.refresh(new_appeal)
    
    return {
        "status": "success", 
        "message": "Обращение сохранено в базе данных",
        "id": new_appeal.id
    }
