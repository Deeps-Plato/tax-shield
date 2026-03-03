import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "securepass123",
        "name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["name"] == "New User"
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, test_user):
    resp = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "anotherpass",
        "name": "Duplicate",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    resp = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid(client: AsyncClient, test_user):
    resp = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient, test_user):
    resp = await client.get("/api/auth/me", headers=test_user["headers"])
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_me_no_auth(client: AsyncClient):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, test_user):
    resp = await client.post("/api/auth/change-password", json={
        "current_password": "testpass123",
        "new_password": "newpass456",
    }, headers=test_user["headers"])
    assert resp.status_code == 204

    # Login with new password
    resp = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "newpass456",
    })
    assert resp.status_code == 200
