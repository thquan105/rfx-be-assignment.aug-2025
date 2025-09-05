from datetime import date

import pytest
from httpx import AsyncClient


async def setup_project_with_tasks(client: AsyncClient):
    # Register admin
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "org_name": "OrgReports",
            "email": "adminreports@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 200
    admin_token = resp.json()["token"]["access_token"]

    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "ReportProj"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_proj.status_code == 200
    project_id = resp_proj.json()["id"]

    # Create tasks (todo + done)
    await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Task 1", "status": "todo"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Task 2", "status": "done"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    return admin_token, project_id


@pytest.mark.asyncio
async def test_member_cannot_access_reports(client: AsyncClient):
    # Register admin
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "org_name": "OrgReports2",
            "email": "adminrep2@example.com",
            "password": "password123",
        },
    )
    admin_token = resp.json()["token"]["access_token"]

    # Create project
    resp_proj = await client.post(
        "/api/v1/projects",
        json={"name": "Proj2"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    project_id = resp_proj.json()["id"]

    # Create member
    await client.post(
        "/api/v1/users",
        json={
            "email": "memberrep2@example.com",
            "password": "password123",
            "role": "member",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Login as member
    resp_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "memberrep2@example.com", "password": "password123"},
    )
    member_token = resp_login.json()["access_token"]

    # Member calls report → forbidden
    resp_count = await client.get(
        f"/api/v1/projects/{project_id}/report/status-count",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp_count.status_code == 403

    resp_overdue = await client.get(
        f"/api/v1/projects/{project_id}/report/overdue-tasks",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp_overdue.status_code == 403


@pytest.mark.asyncio
async def test_report_project_not_found(client: AsyncClient):
    # Register admin
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "org_name": "OrgReports3",
            "email": "adminrep3@example.com",
            "password": "password123",
        },
    )
    admin_token = resp.json()["token"]["access_token"]

    # Call report on non-existing project
    resp_count = await client.get(
        "/api/v1/projects/9999/report/status-count",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_count.status_code == 404

    resp_overdue = await client.get(
        "/api/v1/projects/9999/report/overdue-tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_overdue.status_code == 404
