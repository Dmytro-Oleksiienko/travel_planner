"""Tests for Travel Project API endpoints."""

import pytest


class TestCreateProject:
    """Tests for POST /api/v1/projects."""

    def test_create_project_minimal(self, client):
        """Create a project with only required fields."""
        response = client.post(
            "/api/v1/projects",
            json={"name": "My Trip"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Trip"
        assert data["description"] is None
        assert data["start_date"] is None
        assert data["status"] == "planning"
        assert "id" in data
        assert "created_at" in data

    def test_create_project_full(self, client):
        """Create a project with all fields."""
        response = client.post(
            "/api/v1/projects",
            json={
                "name": "Europe Tour",
                "description": "Summer trip to Europe",
                "start_date": "2026-07-01",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Europe Tour"
        assert data["description"] == "Summer trip to Europe"
        assert data["start_date"] == "2026-07-01"

    def test_create_project_empty_name(self, client):
        """Creating a project with empty name should fail."""
        response = client.post(
            "/api/v1/projects",
            json={"name": ""},
        )
        assert response.status_code == 422

    def test_create_project_missing_name(self, client):
        """Creating a project without name should fail."""
        response = client.post(
            "/api/v1/projects",
            json={"description": "No name"},
        )
        assert response.status_code == 422


class TestListProjects:
    """Tests for GET /api/v1/projects."""

    def test_list_projects_empty(self, client):
        """List projects when none exist."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_projects_with_data(self, client):
        """List projects with existing data."""
        # Create projects
        client.post("/api/v1/projects", json={"name": "Trip 1"})
        client.post("/api/v1/projects", json={"name": "Trip 2"})

        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_projects_pagination(self, client):
        """Test pagination works correctly."""
        # Create 3 projects
        for i in range(3):
            client.post("/api/v1/projects", json={"name": f"Trip {i}"})

        response = client.get("/api/v1/projects?page=1&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["pages"] == 2

    def test_list_projects_search(self, client):
        """Test search filter."""
        client.post("/api/v1/projects", json={"name": "Europe Tour"})
        client.post("/api/v1/projects", json={"name": "Asia Trip"})

        response = client.get("/api/v1/projects?search=europe")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Europe Tour"


class TestGetProject:
    """Tests for GET /api/v1/projects/{id}."""

    def test_get_project(self, client, sample_project):
        """Get an existing project."""
        project_id = sample_project["id"]
        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "Test Trip"

    def test_get_project_not_found(self, client):
        """Get a non-existent project."""
        response = client.get("/api/v1/projects/999")
        assert response.status_code == 404


class TestUpdateProject:
    """Tests for PUT /api/v1/projects/{id}."""

    def test_update_project_name(self, client, sample_project):
        """Update a project's name."""
        project_id = sample_project["id"]
        response = client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "Updated Trip"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Trip"

    def test_update_project_not_found(self, client):
        """Update a non-existent project."""
        response = client.put(
            "/api/v1/projects/999",
            json={"name": "Updated"},
        )
        assert response.status_code == 404


class TestDeleteProject:
    """Tests for DELETE /api/v1/projects/{id}."""

    def test_delete_project(self, client, sample_project):
        """Delete a project without visited places."""
        project_id = sample_project["id"]
        response = client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == 404

    def test_delete_project_not_found(self, client):
        """Delete a non-existent project."""
        response = client.delete("/api/v1/projects/999")
        assert response.status_code == 404
