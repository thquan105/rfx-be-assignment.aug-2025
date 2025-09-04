import pytest
from httpx import AsyncClient


async def register_and_login(
    client: AsyncClient,
    email="projadmin@example.com",
    password="password123",
    org_name="OrgProj",
):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"org_name": org_name, "email": email, "password": password},
    )
    assert resp.status_code == 200
    token = resp.json()["token"]["access_token"]
    user_id = resp.json()["admin"]["id"]
    return token, user_id


@pytest.mark.asyncio
async def test_create_and_list_projects(client: AsyncClient):
    token, _ = await register_and_login(client, "projectuser@example.com")
    # Create project
    resp = await client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "description": "Project description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Project"

    # List projects
    resp_list = await client.get(
        "/api/v1/projects", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_list.status_code == 200
    projects = resp_list.json()
    assert any(p["name"] == "Test Project" for p in projects)


@pytest.mark.asyncio
async def test_get_project_detail_and_forbidden(client: AsyncClient):
    token, _ = await register_and_login(
        client, "projectdetail@example.com", org_name="OrgA"
    )
    resp = await client.post(
        "/api/v1/projects",
        json={"name": "DetailProj"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = resp.json()["id"]

    # Get detail success
    resp_get = await client.get(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_get.status_code == 200
    assert resp_get.json()["name"] == "DetailProj"

    # Register another user in different org
    token_other, _ = await register_and_login(
        client, "other@example.com", org_name="OrgB"
    )
    resp_get_forbidden = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token_other}"},
    )
    assert resp_get_forbidden.status_code == 404


@pytest.mark.asyncio
async def test_add_and_remove_members(client: AsyncClient):
    admin_token, admin_id = await register_and_login(
        client, "adminproj@example.com", org_name="OrgC"
    )
    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "TeamProj"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    project_id = resp_proj.json()["id"]

    # Create new user in same org
    resp_user = await client.post(
        "/api/v1/users",
        json={
            "email": "memberproj@example.com",
            "password": "password123",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_id = resp_user.json()["id"]

    # Add member
    resp_add = await client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_ids": [user_id]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_add.status_code == 200
    members = resp_add.json()
    assert any(m["email"] == "memberproj@example.com" for m in members)

    # Remove member
    resp_del = await client.delete(
        f"/api/v1/projects/{project_id}/members/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_del.status_code == 204

    # Cannot remove self
    resp_del_self = await client.delete(
        f"/api/v1/projects/{project_id}/members/{admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_del_self.status_code == 400


@pytest.mark.asyncio
async def test_list_project_members(client: AsyncClient):
    token, _ = await register_and_login(
        client, "memberlist@example.com", org_name="OrgD"
    )
    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "ListProj"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = resp_proj.json()["id"]

    # List members
    resp_list = await client.get(
        f"/api/v1/projects/{project_id}/members",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_list.status_code == 200
    members = resp_list.json()
    assert any(m["email"] == "memberlist@example.com" for m in members)
