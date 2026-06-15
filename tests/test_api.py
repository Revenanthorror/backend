import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Сервер успешно запущен" in response.json()["message"]

@pytest.mark.asyncio
async def test_calculate_validation(client):
    response = await client.post("/calculate/", json={"numbers": [1], "delays": ["invalid"]})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_calculate_success(client):
    response = await client.post("/calculate/", json={"numbers": [4, 5], "delays": [0.1, 0.2]})
    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["square"] == 16
    assert data["results"][1]["square"] == 25
    assert "total_time" in data

@pytest.mark.asyncio
async def test_submit_appeal_unauthorized(client):
    response = await client.post("/appeals/", json={
        "last_name": "Иванов",
        "first_name": "Иван",
        "birth_date": "1990-01-01",
        "phone": "+79991234567",
        "email": "ivan@example.com"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/auth/register", json={
        "username": "newuser",
        "password": "newpass123"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"

@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post("/auth/register", json={"username": "dupuser", "password": "pass123"})
    response = await client.post("/auth/register", json={"username": "dupuser", "password": "pass123"})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_and_me(client):
    await client.post("/auth/register", json={"username": "logintest", "password": "testpass123"})
    login = await client.post("/auth/login", data={"username": "logintest", "password": "testpass123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "logintest"
    assert me.json()["role"] == "user"

@pytest.mark.asyncio
async def test_create_appeal_authorized(auth_client):
    response = await auth_client.post("/appeals/", json={
        "last_name": "Петров",
        "first_name": "Петр",
        "birth_date": "1985-05-05",
        "phone": "+79991112233",
        "email": "petr@example.com"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["last_name"] == "Петров"
    assert data["user_id"] is not None

@pytest.mark.asyncio
async def test_list_appeals_user_only_own(client):
    for u in ["user1", "user2"]:
        await client.post("/auth/register", json={"username": u, "password": "testpass123"})

    login1 = await client.post("/auth/login", data={"username": "user1", "password": "testpass123"})
    token1 = login1.json()["access_token"]

    await client.post("/appeals/", json={
        "last_name": "Сидоров",
        "first_name": "Сидор",
        "birth_date": "1990-01-01",
        "phone": "+79993334455",
        "email": "sidor@example.com"
    }, headers={"Authorization": f"Bearer {token1}"})

    response = await client.get("/appeals/", headers={"Authorization": f"Bearer {token1}"})
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_get_appeal_by_id(auth_client):
    create = await auth_client.post("/appeals/", json={
        "last_name": "Кузнецов",
        "first_name": "Кузьма",
        "birth_date": "1992-02-02",
        "phone": "+79994445566",
        "email": "kuzma@example.com"
    })
    appeal_id = create.json()["id"]

    response = await auth_client.get(f"/appeals/{appeal_id}")
    assert response.status_code == 200
    assert response.json()["id"] == appeal_id

@pytest.mark.asyncio
async def test_delete_appeal(auth_client):
    create = await auth_client.post("/appeals/", json={
        "last_name": "Удалов",
        "first_name": "Удал",
        "birth_date": "1993-03-03",
        "phone": "+79995556677",
        "email": "delete@example.com"
    })
    appeal_id = create.json()["id"]

    response = await auth_client.delete(f"/appeals/{appeal_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/appeals/{appeal_id}")
    assert get_resp.status_code == 404

@pytest.mark.asyncio
async def test_sql_injection_safe(client):
    res = await client.post("/auth/login", data={
        "username": "' OR 1=1 --",
        "password": "x"
    })
    assert res.status_code in [400, 401]
    assert res.status_code != 200

@pytest.mark.asyncio
async def test_phone_validation(auth_client):
    response = await auth_client.post("/appeals/", json={
        "last_name": "Иванов",
        "first_name": "Иван",
        "birth_date": "1990-01-01",
        "phone": "123",
        "email": "ivan@example.com"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_name_validation(auth_client):
    response = await auth_client.post("/appeals/", json={
        "last_name": "ivanov",
        "first_name": "Иван",
        "birth_date": "1990-01-01",
        "phone": "+79991234567",
        "email": "ivan@example.com"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_change_password(client):
    await client.post("/auth/register", json={"username": "passuser", "password": "oldpass123"})
    login = await client.post("/auth/login", data={"username": "passuser", "password": "oldpass123"})
    token = login.json()["access_token"]

    response = await client.post("/auth/change-password", params={
        "old_password": "oldpass123",
        "new_password": "newpass456"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    old_login = await client.post("/auth/login", data={"username": "passuser", "password": "oldpass123"})
    assert old_login.status_code == 400

    new_login = await client.post("/auth/login", data={"username": "passuser", "password": "newpass456"})
    assert new_login.status_code == 200
