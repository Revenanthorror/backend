from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.models import User
from app.schemas.schemas import UserCreate, Token

router = APIRouter(prefix="/auth", tags=["auth"])

# Настройка схемы OAuth2 для извлечения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Регистрация нового пользователя")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрирует нового пользователя в системе.
    Проверяет уникальность username и хэширует пароль.
    """
    # Проверка, существует ли уже пользователь с таким именем
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Хэширование пароля перед сохранением в БД (защита данных)
    hashed_pwd = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pwd)
    
    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully"}

@router.post("/login", response_model=Token, summary="Аутентификация и получение токена")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Аутентифицирует пользователя по username и password.
    Возвращает JWT access-токен в случае успеха.
    """
    # Поиск пользователя в БД
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    # Проверка существования пользователя и валидности хэша пароля
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Генерация JWT-токена с ограниченным сроком действия
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Зависимость (Dependency) для защиты эндпоинтов.
    Декодирует JWT-токен, валидирует его и извлекает пользователя из БД.
    """
    # Стандартное исключение для неавторизованных запросов
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен при помощи секретного ключа системы
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # Если токен изменен, просрочен или поврежден — выбрасываем ошибку
        raise credentials_exception
        
    # Извлекаем пользователя из базы данных для проверки его существования
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
        
    return user