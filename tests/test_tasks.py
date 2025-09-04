import pytest
from httpx import AsyncClient


async def register_and_login(
    client: AsyncClient, email, password="password123", org_name="OrgTasks"
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
async def test_create_task_and_list(client: AsyncClient):
    token, _ = await register_and_login(client, "taskcreator@example.com")
    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "TaskProj"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = resp_proj.json()["id"]

    # Create task
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Test Task", "description": "Do something"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_task.status_code == 200
    data = resp_task.json()
    assert data["title"] == "Test Task"

    # List tasks
    resp_list = await client.get(
        f"/api/v1/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_list.status_code == 200
    tasks = resp_list.json()
    assert any(t["title"] == "Test Task" for t in tasks)


@pytest.mark.asyncio
async def test_admin_assign_task(client: AsyncClient):
    admin_token, _ = await register_and_login(
        client, "admintask@example.com", org_name="OrgAssign"
    )
    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "AssignProj"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    project_id = resp_proj.json()["id"]

    # Create member in same org
    resp_user = await client.post(
        "/api/v1/users",
        json={
            "email": "membertask@example.com",
            "password": "password123",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    member_id = resp_user.json()["id"]

    # Admin assign task to member
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={
            "title": "Assigned Task",
            "description": "Admin assigns",
            "assignee_id": member_id,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_task.status_code == 200
    assert resp_task.json()["assignee_id"] == member_id

@pytest.mark.asyncio
async def test_get_task_not_found(client: AsyncClient):
    token, _ = await register_and_login(client, "tasknf@example.com")
    resp = await client.get("/api/v1/tasks/9999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_update_status_forward_and_backward(client: AsyncClient):
    token, _ = await register_and_login(
        client, "statususer@example.com", org_name="OrgStatus"
    )
    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "StatusProj"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = resp_proj.json()["id"]

    # Create task
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Status Task", "description": "Check status"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = resp_task.json()["id"]

    # Update forward: todo -> in-progress
    resp_update = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "in-progress"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["status"] == "in-progress"

    # Update backward: in-progress -> todo (invalid)
    resp_back = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "todo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_back.status_code == 400
