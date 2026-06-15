from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Appeal, User
from app.schemas.schemas import AppealCreate

class AppealService:
    """Сервисный слой для бизнес-логики обращений."""

    @staticmethod
    async def create_appeal(db: AsyncSession, appeal_data: AppealCreate, user_id: int) -> Appeal:
        new_appeal = Appeal(user_id=user_id, **appeal_data.model_dump())
        db.add(new_appeal)
        await db.commit()
        await db.refresh(new_appeal)
        return new_appeal

    @staticmethod
    async def get_appeals(db: AsyncSession, user: User, skip: int = 0, limit: int = 100):
        if user.role == "admin":
            result = await db.execute(select(Appeal).offset(skip).limit(limit))
        else:
            result = await db.execute(
                select(Appeal).where(Appeal.user_id == user.id).offset(skip).limit(limit)
            )
        return result.scalars().all()

    @staticmethod
    async def get_appeal(db: AsyncSession, appeal_id: int, user: User):
        result = await db.execute(select(Appeal).where(Appeal.id == appeal_id))
        appeal = result.scalars().first()
        if not appeal:
            return None
        if user.role != "admin" and appeal.user_id != user.id:
            return None
        return appeal

    @staticmethod
    async def delete_appeal(db: AsyncSession, appeal_id: int, user: User) -> bool:
        result = await db.execute(select(Appeal).where(Appeal.id == appeal_id))
        appeal = result.scalars().first()
        if not appeal:
            return False
        if user.role != "admin" and appeal.user_id != user.id:
            return False
        await db.delete(appeal)
        await db.commit()
        return True
