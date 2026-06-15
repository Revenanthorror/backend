from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import AppealCreate, AppealResponse
from app.core.security import get_current_user
from app.services.appeals import AppealService

router = APIRouter(prefix="/appeals", tags=["appeals"])

@router.post(
    "/",
    response_model=AppealResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать обращение (требует авторизации)"
)
async def submit_appeal(
    appeal_data: AppealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создает новое обращение, привязывая его к текущему пользователю."""
    appeal = await AppealService.create_appeal(db, appeal_data, current_user.id)
    return appeal

@router.get(
    "/",
    response_model=List[AppealResponse],
    summary="Получить список обращений"
)
async def list_appeals(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin видит все обращения, user — только свои."""
    appeals = await AppealService.get_appeals(db, current_user, skip, limit)
    return appeals

@router.get(
    "/{appeal_id}",
    response_model=AppealResponse,
    summary="Получить обращение по ID"
)
async def get_appeal(
    appeal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin видит любое обращение, user — только свое."""
    appeal = await AppealService.get_appeal(db, appeal_id, current_user)
    if not appeal:
        raise HTTPException(status_code=404, detail="Обращение не найдено или доступ запрещен")
    return appeal

@router.delete(
    "/{appeal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить обращение"
)
async def delete_appeal(
    appeal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin может удалить любое обращение, user — только свое."""
    success = await AppealService.delete_appeal(db, appeal_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Обращение не найдено или доступ запрещен")
    return None
