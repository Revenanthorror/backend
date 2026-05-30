import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Сервер успешно запущен" in response.json()["message"]

@pytest.mark.asyncio
async def test_calculate_validation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/calculate/", json={"numbers": [1], "delays": ["invalid"]})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_calculate_success():
    """Тест успешной бизнес-логики вычислений"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/calculate/", json={
            "numbers": [4, 5], 
            "delays": [0.1, 0.2]
        })
    
    assert response.status_code == 200
    data = response.json()
    # Проверяем, что математика работает верно
    assert data["results"][0]["square"] == 16
    assert data["results"][1]["square"] == 25
    # Проверяем, что вернулось общее время
    assert "total_time" in data


@pytest.mark.asyncio
async def test_submit_appeal_unauthorized():
    """Тест защиты маршрута: попытка отправить заявку без токена"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/appeals/", json={
            "last_name": "Иванов",
            "first_name": "Иван",
            "birth_date": "1990-01-01",
            "phone": "+79991234567",
            "email": "ivan@example.com"
        })
    
    # Должен отбить запрос, так как мы не передали токен в заголовках
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"