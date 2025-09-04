import pytest
from httpx import AsyncClient


async def setup_org_and_users(client: AsyncClient):
    # Register admin
    resp = await client.post(
        "/api/v1/auth/register",
        json={"org_name": "OrgNoti", "email": "adminnoti@example.com", "password": "password123"}
    )
    admin_token = resp.json()["token"]["access_token"]

    # Create member
    resp_member = await client.post(
        "/api/v1/users",
        json={"email": "notimember@example.com", "password": "password123", "role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    member_id = resp_member.json()["id"]

    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "NotiProj"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    project_id = resp_proj.json()["id"]

    # Add member to project
    await client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_ids": [member_id]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Login as member
    resp_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "notimember@example.com", "password": "password123"}
    )
    member_token = resp_login.json()["access_token"]

    return admin_token, member_token, member_id, project_id


@pytest.mark.asyncio
async def test_assignment_notification(client: AsyncClient):
    admin_token, member_token, member_id, project_id = await setup_org_and_users(client)

    # Admin create task and assign to member -> notification created
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Assigned Task", "description": "Testing noti", "assignee_id": member_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_task.status_code == 200

    # Member fetch unread notifications
    resp = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any(n["type"] == "assignment" for n in data)


@pytest.mark.asyncio
async def test_status_change_notification(client: AsyncClient):
    admin_token, member_token, member_id, project_id = await setup_org_and_users(client)

    # Admin create task assigned to member
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Status Task", "description": "Change status", "assignee_id": member_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    task_id = resp_task.json()["id"]

    # Admin update status -> notification for member
    resp_update = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "in-progress"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_update.status_code == 200

    resp = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any(n["type"] == "status_change" for n in data)


@pytest.mark.asyncio
async def test_comment_notification(client: AsyncClient):
    admin_token, member_token, member_id, project_id = await setup_org_and_users(client)

    # Admin create task assigned to member
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Comment Task", "description": "Trigger comment noti", "assignee_id": member_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    task_id = resp_task.json()["id"]

    # Admin comment on task -> notification for member
    resp_comment = await client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "Good job!"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_comment.status_code == 200

    resp = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    data = resp.json()
    assert any(n["type"] == "comment_added" for n in data)


@pytest.mark.asyncio
async def test_mark_read_and_read_all(client: AsyncClient):
    admin_token, member_token, member_id, project_id = await setup_org_and_users(client)

    # Admin create task assigned to member
    resp_task = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Mark Read Task", "description": "Notifications demo", "assignee_id": member_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_task.status_code == 200

    # Get notifications
    resp = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    data = resp.json()
    assert len(data) > 0
    notif_id = data[0]["id"]

    # Mark one notification read
    resp_patch = await client.patch(
        f"/api/v1/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert resp_patch.status_code == 200
    assert resp_patch.json()["is_read"] is True

    # Mark all as read
    resp_patch_all = await client.patch(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert resp_patch_all.status_code == 200
    assert "updated" in resp_patch_all.json()
