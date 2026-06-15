import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.models import User
from app.core.security import get_password_hash

async def create_admin(username: str = "admin", password: str = "admin123"):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if user:
            user.role = "admin"
            user.hashed_password = get_password_hash(password)
            await session.commit()
            print(f"Admin '{username}' updated")
        else:
            admin = User(
                username=username,
                hashed_password=get_password_hash(password),
                role="admin"
            )
            session.add(admin)
            await session.commit()
            print(f"Admin '{username}' created with password '{password}'")

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    asyncio.run(create_admin(username, password))
