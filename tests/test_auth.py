import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "org_name": "TestOrg",
            "email": "authuser@example.com",
            "password": "password123",
            "full_name": "Auth User",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["organization"]["name"] == "TestOrg"
    assert data["admin"]["email"] == "authuser@example.com"
    assert "access_token" in data["token"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "org_name": "DupOrg",
        "email": "dup@example.com",
        "password": "password123",
        "full_name": "Dup User",
    }
    # First register
    await client.post("/api/v1/auth/register", json=payload)
    # Second register with same email
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400 or resp.status_code == 409


@pytest.mark.asyncio
async def test_login_valid(client: AsyncClient):
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "org_name": "LoginOrg",
            "email": "login@example.com",
            "password": "password123",
        },
    )
    # Login
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "org_name": "WrongPassOrg",
            "email": "wrongpass@example.com",
            "password": "correctpassword",
        },
    )
    # Wrong password
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
