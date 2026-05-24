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
