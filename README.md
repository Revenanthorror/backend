# FastAPI Final Project

Итоговый проект по курсу «Разработка веб-сервисов и приложений».

## Реализованный функционал
* Асинхронное API на FastAPI с декомпозированной структурой (routers / schemas / services / core).
* База данных PostgreSQL (подключена через SQLAlchemy ORM + asyncpg).
* Настроены миграции Alembic.
* JWT-аутентификация (регистрация, логин, /me, смена пароля).
* **RBAC** — ролевая модель доступа (user / admin).
* **Сервисный слой** — бизнес-логика вынесена из роутеров в `app/services/`.
* Полный CRUD обращений (appeals) с разграничением прав: admin видит все, user — только свои.
* Валидация данных с кастомными правилами на Pydantic V2 (кириллица, российский телефон, дата в прошлом).
* Защита от SQL-инъекций через ORM-параметризацию.
* Асинхронные вычисления (`asyncio.gather`) с демонстрацией прироста скорости.
* Развертывание в изолированной среде через Docker Compose.
* Pytest автотесты (15+ тестов) с покрытием валидации, авторизации, RBAC, SQL-инъекций.

## Запуск проекта
```bash
docker compose up -d --build
```

## Создание администратора
```bash
docker exec -it <web_container> python make_admin.py admin admin123
```

## Запуск тестов
```bash
docker exec -it backend-web-1 pytest -v
```

## Структура проекта
```
app/
  core/         # config, database, security (JWT, bcrypt, RBAC)
  models/       # SQLAlchemy модели (User, Appeal)
  schemas/      # Pydantic-схемы валидации
  services/     # Бизнес-логика (AppealService)
  routers/      # FastAPI-эндпоинты
  main.py       # Точка входа
tests/          # Pytest тесты
alembic/        # Миграции БД
```

## API Endpoints
| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | /auth/register | Регистрация | Все |
| POST | /auth/login | Логин + JWT | Все |
| GET | /auth/me | Текущий пользователь | Авторизованные |
| POST | /auth/change-password | Смена пароля | Авторизованные |
| POST | /appeals/ | Создать обращение | Авторизованные |
| GET | /appeals/ | Список обращений | Авторизованные (RBAC) |
| GET | /appeals/{id} | Получить обращение | Авторизованные (RBAC) |
| DELETE | /appeals/{id} | Удалить обращение | Авторизованные (RBAC) |
| POST | /calculate/ | Асинхронные вычисления | Все |
