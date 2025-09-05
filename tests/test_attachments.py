import io

import pytest
from httpx import AsyncClient


async def setup_project_and_task(client: AsyncClient):
    # Register admin
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "org_name": "OrgAttachments",
            "email": "adminattach@example.com",
            "password": "password123",
        },
    )
    admin_token = resp.json()["token"]["access_token"]

    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "AttachProj"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    project_id = resp_proj.json()["id"]

    # Create task
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Task for attachments"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    task_id = resp_task.json()["id"]

    return admin_token, project_id, task_id


@pytest.mark.asyncio
async def test_member_upload_attachment_success(client: AsyncClient):
    admin_token, project_id, task_id = await setup_project_and_task(client)

    # Create member
    resp_member = await client.post(
        "/api/v1/users",
        json={
            "email": "uploader@example.com",
            "password": "password123",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    member_id = resp_member.json()["id"]

    # Add member to project
    await client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_ids": [member_id]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Login as member
    resp_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "uploader@example.com", "password": "password123"},
    )
    token = resp_login.json()["access_token"]

    # Upload file
    file_content = b"dummy data"
    resp = await client.post(
        f"/api/v1/tasks/{task_id}/attachments",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("dummy.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert resp.status_code == 200
    assert resp.json()["file_name"] == "dummy.txt"
