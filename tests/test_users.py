import pytest
from httpx import AsyncClient


async def _register_and_login(
    client: AsyncClient, email="user@example.com", password="password123"
):
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={"org_name": "UserOrg", "email": email, "password": password},
    )
    # Login
    resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    token = resp.json()["access_token"]
    return token


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    token = await _register_and_login(client, "me@example.com")
    resp = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient):
    token = await _register_and_login(client, "changepass@example.com", "oldpass")
    # Change password
    resp = await client.patch(
        "/api/v1/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "oldpass", "new_password": "newpass123"},
    )
    assert resp.status_code == 200
    assert resp.json()["msg"] == "Password updated successfully"


@pytest.mark.asyncio
async def test_change_password_fail_wrong_current(client: AsyncClient):
    token = await _register_and_login(client, "wrongchangepass@example.com", "goodpass")
    # Wrong current password
    resp = await client.patch(
        "/api/v1/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "badpass", "new_password": "newpass"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Current password is incorrect"
