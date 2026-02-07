# Task: T-014 - Write Backend Integration Tests
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Integration tests for Task CRUD endpoints.

Tests all 6 task endpoints with various scenarios:
- Valid operations
- Authentication failures (401)
- Authorization failures (403)
- Not found scenarios (404)
- Validation errors (422)
- User isolation
"""

import pytest
from httpx import AsyncClient


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test basic health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "todo-api"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test API root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Todo API"
        assert "version" in data
        assert "docs" in data


# =============================================================================
# List Tasks Tests (GET /{user_id}/tasks)
# =============================================================================

class TestListTasks:
    """Tests for GET /{user_id}/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing tasks when none exist."""
        response = await client.get(
            "/api/test-user-123/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_tasks_with_data(self, client: AsyncClient, auth_headers: dict):
        """Test listing tasks after creating some."""
        # Create tasks
        await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Task 1"},
        )
        await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Task 2"},
        )

        response = await client.get(
            "/api/test-user-123/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_filter_pending(self, client: AsyncClient, auth_headers: dict):
        """Test filtering tasks by pending status."""
        # Create tasks
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Pending Task"},
        )
        task_id = create_resp.json()["id"]

        # Complete one task
        await client.patch(
            f"/api/test-user-123/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Another Pending"},
        )

        response = await client.get(
            "/api/test-user-123/tasks?status=pending",
            headers=auth_headers,
        )

        assert response.status_code == 200
        tasks = response.json()
        assert all(not t["completed"] for t in tasks)

    @pytest.mark.asyncio
    async def test_list_tasks_filter_completed(self, client: AsyncClient, auth_headers: dict):
        """Test filtering tasks by completed status."""
        # Create and complete a task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Will Complete"},
        )
        task_id = create_resp.json()["id"]

        await client.patch(
            f"/api/test-user-123/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        response = await client.get(
            "/api/test-user-123/tasks?status=completed",
            headers=auth_headers,
        )

        assert response.status_code == 200
        tasks = response.json()
        assert all(t["completed"] for t in tasks)

    @pytest.mark.asyncio
    async def test_list_tasks_unauthorized(self, client: AsyncClient):
        """Test listing tasks without authentication."""
        response = await client.get("/api/test-user-123/tasks")

        assert response.status_code == 401  # JWT verification returns 401 when no auth

    @pytest.mark.asyncio
    async def test_list_tasks_wrong_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing tasks for different user (403)."""
        response = await client.get(
            "/api/other-user-456/tasks",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()


# =============================================================================
# Create Task Tests (POST /{user_id}/tasks)
# =============================================================================

class TestCreateTask:
    """Tests for POST /{user_id}/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client: AsyncClient, auth_headers: dict):
        """Test creating a task with valid data."""
        response = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is False
        assert data["user_id"] == "test-user-123"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_task_title_only(self, client: AsyncClient, auth_headers: dict):
        """Test creating a task with title only."""
        response = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Simple task"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Simple task"
        assert data["description"] is None

    @pytest.mark.asyncio
    async def test_create_task_missing_title(self, client: AsyncClient, auth_headers: dict):
        """Test creating a task without title (422)."""
        response = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"description": "No title"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_empty_title(self, client: AsyncClient, auth_headers: dict):
        """Test creating a task with empty title (422)."""
        response = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": ""},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_title_too_long(self, client: AsyncClient, auth_headers: dict):
        """Test creating a task with title over 200 chars (422)."""
        response = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "a" * 201},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_description_too_long(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating a task with description over 1000 chars (422)."""
        response = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={
                "title": "Valid title",
                "description": "a" * 1001,
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_unauthorized(self, client: AsyncClient):
        """Test creating a task without authentication."""
        response = await client.post(
            "/api/test-user-123/tasks",
            json={"title": "Test"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_task_wrong_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating a task for different user (403)."""
        response = await client.post(
            "/api/other-user-456/tasks",
            headers=auth_headers,
            json={"title": "Test"},
        )

        assert response.status_code == 403


# =============================================================================
# Get Task Tests (GET /{user_id}/tasks/{task_id})
# =============================================================================

class TestGetTask:
    """Tests for GET /{user_id}/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_task_success(self, client: AsyncClient, auth_headers: dict):
        """Test getting a task by ID."""
        # Create task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Test Task", "description": "Test description"},
        )
        task_id = create_resp.json()["id"]

        # Get task
        response = await client.get(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert data["description"] == "Test description"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting a non-existent task (404)."""
        response = await client.get(
            "/api/test-user-123/tasks/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_task_unauthorized(self, client: AsyncClient):
        """Test getting a task without authentication."""
        response = await client.get("/api/test-user-123/tasks/1")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_task_wrong_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting a task belonging to different user."""
        response = await client.get(
            "/api/other-user-456/tasks/1",
            headers=auth_headers,
        )

        assert response.status_code == 403


# =============================================================================
# Update Task Tests (PUT /{user_id}/tasks/{task_id})
# =============================================================================

class TestUpdateTask:
    """Tests for PUT /{user_id}/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_success(self, client: AsyncClient, auth_headers: dict):
        """Test updating a task."""
        # Create task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Original Title"},
        )
        task_id = create_resp.json()["id"]

        # Update task
        response = await client.put(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "description": "New description",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_task_partial(self, client: AsyncClient, auth_headers: dict):
        """Test updating only some fields."""
        # Create task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Original", "description": "Original desc"},
        )
        task_id = create_resp.json()["id"]

        # Update only title
        response = await client.put(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
            json={"title": "New Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        # Description should remain unchanged
        assert data["description"] == "Original desc"

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating a non-existent task (404)."""
        response = await client.put(
            "/api/test-user-123/tasks/99999",
            headers=auth_headers,
            json={"title": "New Title"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task_invalid_title(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test updating with invalid title (422)."""
        # Create task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Original"},
        )
        task_id = create_resp.json()["id"]

        # Update with too long title
        response = await client.put(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
            json={"title": "a" * 201},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_task_unauthorized(self, client: AsyncClient):
        """Test updating a task without authentication."""
        response = await client.put(
            "/api/test-user-123/tasks/1",
            json={"title": "New Title"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_task_wrong_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test updating a task belonging to different user."""
        response = await client.put(
            "/api/other-user-456/tasks/1",
            headers=auth_headers,
            json={"title": "New Title"},
        )

        assert response.status_code == 403


# =============================================================================
# Delete Task Tests (DELETE /{user_id}/tasks/{task_id})
# =============================================================================

class TestDeleteTask:
    """Tests for DELETE /{user_id}/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a task."""
        # Create task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "To Delete"},
        )
        task_id = create_resp.json()["id"]

        # Delete task
        response = await client.delete(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        get_resp = await client.get(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a non-existent task (404)."""
        response = await client.delete(
            "/api/test-user-123/tasks/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_unauthorized(self, client: AsyncClient):
        """Test deleting a task without authentication."""
        response = await client.delete("/api/test-user-123/tasks/1")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_task_wrong_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test deleting a task belonging to different user."""
        response = await client.delete(
            "/api/other-user-456/tasks/1",
            headers=auth_headers,
        )

        assert response.status_code == 403


# =============================================================================
# Toggle Complete Tests (PATCH /{user_id}/tasks/{task_id}/complete)
# =============================================================================

class TestToggleComplete:
    """Tests for PATCH /{user_id}/tasks/{task_id}/complete endpoint."""

    @pytest.mark.asyncio
    async def test_toggle_complete_to_true(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test marking a task as complete."""
        # Create task (starts as incomplete)
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Toggle Test"},
        )
        task_id = create_resp.json()["id"]
        assert create_resp.json()["completed"] is False

        # Toggle to complete
        response = await client.patch(
            f"/api/test-user-123/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True

    @pytest.mark.asyncio
    async def test_toggle_complete_to_false(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test marking a completed task as incomplete."""
        # Create and complete task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Toggle Back"},
        )
        task_id = create_resp.json()["id"]

        # Toggle to complete
        await client.patch(
            f"/api/test-user-123/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        # Toggle back to incomplete
        response = await client.patch(
            f"/api/test-user-123/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["completed"] is False

    @pytest.mark.asyncio
    async def test_toggle_complete_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test toggling a non-existent task (404)."""
        response = await client.patch(
            "/api/test-user-123/tasks/99999/complete",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_toggle_complete_unauthorized(self, client: AsyncClient):
        """Test toggling without authentication."""
        response = await client.patch("/api/test-user-123/tasks/1/complete")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_toggle_complete_wrong_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test toggling a task belonging to different user."""
        response = await client.patch(
            "/api/other-user-456/tasks/1/complete",
            headers=auth_headers,
        )

        assert response.status_code == 403


# =============================================================================
# User Isolation Tests
# =============================================================================

class TestUserIsolation:
    """Tests for user data isolation."""

    @pytest.mark.asyncio
    async def test_user_cannot_see_other_users_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_user_headers: dict,
    ):
        """Test that users cannot see each other's tasks."""
        # User 1 creates a task
        await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "User 1 Task"},
        )

        # User 2 creates a task
        await client.post(
            "/api/other-user-456/tasks",
            headers=other_user_headers,
            json={"title": "User 2 Task"},
        )

        # User 1 lists their tasks
        user1_tasks = await client.get(
            "/api/test-user-123/tasks",
            headers=auth_headers,
        )

        # User 2 lists their tasks
        user2_tasks = await client.get(
            "/api/other-user-456/tasks",
            headers=other_user_headers,
        )

        # Each user should only see their own tasks
        user1_titles = [t["title"] for t in user1_tasks.json()]
        user2_titles = [t["title"] for t in user2_tasks.json()]

        assert "User 1 Task" in user1_titles
        assert "User 2 Task" not in user1_titles

        assert "User 2 Task" in user2_titles
        assert "User 1 Task" not in user2_titles

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_users_task_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_user_headers: dict,
    ):
        """Test that users cannot access specific tasks of other users."""
        # User 1 creates a task
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Private Task"},
        )
        task_id = create_resp.json()["id"]

        # User 2 tries to access User 1's task
        # First, they would need to know the task_id exists
        # Even if they try with the correct user_id in URL, auth will fail
        response = await client.get(
            f"/api/test-user-123/tasks/{task_id}",
            headers=other_user_headers,  # User 2's token
        )

        # Should be 403 because user_id in URL doesn't match token
        assert response.status_code == 403


# =============================================================================
# Full CRUD Workflow Test
# =============================================================================

class TestCRUDWorkflow:
    """Test complete CRUD workflow."""

    @pytest.mark.asyncio
    async def test_full_crud_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test complete create, read, update, toggle, delete workflow."""
        # CREATE
        create_resp = await client.post(
            "/api/test-user-123/tasks",
            headers=auth_headers,
            json={"title": "Workflow Task", "description": "Testing CRUD"},
        )
        assert create_resp.status_code == 201
        task_id = create_resp.json()["id"]

        # READ (single)
        get_resp = await client.get(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == "Workflow Task"

        # READ (list)
        list_resp = await client.get(
            "/api/test-user-123/tasks",
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        assert any(t["id"] == task_id for t in list_resp.json())

        # UPDATE
        update_resp = await client.put(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
            json={"title": "Updated Workflow Task"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["title"] == "Updated Workflow Task"

        # TOGGLE COMPLETE
        toggle_resp = await client.patch(
            f"/api/test-user-123/tasks/{task_id}/complete",
            headers=auth_headers,
        )
        assert toggle_resp.status_code == 200
        assert toggle_resp.json()["completed"] is True

        # DELETE
        delete_resp = await client.delete(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
        )
        assert delete_resp.status_code == 204

        # VERIFY DELETION
        verify_resp = await client.get(
            f"/api/test-user-123/tasks/{task_id}",
            headers=auth_headers,
        )
        assert verify_resp.status_code == 404
