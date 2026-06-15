from fastapi import FastAPI
from app.routers import auth, appeals, calculations

app = FastAPI(
    title="Итоговый проект",
    description="API с аутентификацией, RBAC, базой данных и асинхронными вычислениями."
)

app.include_router(auth.router)
app.include_router(appeals.router)
app.include_router(calculations.router)

@app.get("/")
async def root():
    return {"message": "Сервер успешно запущен. Документация доступна по адресу /docs"}
