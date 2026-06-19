"""Tests for Project Places API endpoints."""

from unittest.mock import patch

import pytest


MOCK_ARTWORK = {
    "id": 129884,
    "title": "Starry Night and the Astronauts",
    "artist_display": "Alma Thomas\nAmerican, 1891–1978",
}

MOCK_ARTWORK_2 = {
    "id": 27992,
    "title": "A Sunday on La Grande Jatte — 1884",
    "artist_display": "Georges Seurat\nFrench, 1859-1891",
}


class TestAddPlace:
    """Tests for POST /api/v1/projects/{project_id}/places."""

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_add_place(self, mock_validate, client, sample_project):
        """Add a valid place to a project."""
        mock_validate.return_value = MOCK_ARTWORK
        project_id = sample_project["id"]

        response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["external_id"] == 129884
        assert data["title"] == "Starry Night and the Astronauts"
        assert data["visited"] is False
        assert data["notes"] is None

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_add_duplicate_place(self, mock_validate, client, sample_project):
        """Adding the same place twice should fail."""
        mock_validate.return_value = MOCK_ARTWORK
        project_id = sample_project["id"]

        # Add first time
        client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )

        # Add again
        response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )
        assert response.status_code == 409

    def test_add_place_project_not_found(self, client):
        """Adding a place to non-existent project should fail."""
        response = client.post(
            "/api/v1/projects/999/places",
            json={"external_id": 129884},
        )
        assert response.status_code == 404

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_add_place_max_limit(self, mock_validate, client, sample_project):
        """Adding more than 10 places should fail."""
        project_id = sample_project["id"]

        # Add 10 places
        for i in range(10):
            mock_validate.return_value = {
                "id": 1000 + i,
                "title": f"Artwork {i}",
                "artist_display": "Artist",
            }
            response = client.post(
                f"/api/v1/projects/{project_id}/places",
                json={"external_id": 1000 + i},
            )
            assert response.status_code == 201

        # Try adding 11th
        mock_validate.return_value = {
            "id": 9999,
            "title": "One Too Many",
            "artist_display": "Artist",
        }
        response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 9999},
        )
        assert response.status_code == 400


class TestListPlaces:
    """Tests for GET /api/v1/projects/{project_id}/places."""

    def test_list_places_empty(self, client, sample_project):
        """List places when none exist in project."""
        project_id = sample_project["id"]
        response = client.get(f"/api/v1/projects/{project_id}/places")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_list_places_with_data(self, mock_validate, client, sample_project):
        """List places with existing data."""
        project_id = sample_project["id"]

        mock_validate.return_value = MOCK_ARTWORK
        client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )

        response = client.get(f"/api/v1/projects/{project_id}/places")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_list_places_project_not_found(self, client):
        """List places for non-existent project."""
        response = client.get("/api/v1/projects/999/places")
        assert response.status_code == 404


class TestGetPlace:
    """Tests for GET /api/v1/projects/{project_id}/places/{place_id}."""

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_get_place(self, mock_validate, client, sample_project):
        """Get a specific place."""
        mock_validate.return_value = MOCK_ARTWORK
        project_id = sample_project["id"]

        # Add a place
        place_response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )
        place_id = place_response.json()["id"]

        # Get the place
        response = client.get(
            f"/api/v1/projects/{project_id}/places/{place_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["external_id"] == 129884

    def test_get_place_not_found(self, client, sample_project):
        """Get a non-existent place."""
        project_id = sample_project["id"]
        response = client.get(
            f"/api/v1/projects/{project_id}/places/999"
        )
        assert response.status_code == 404


class TestUpdatePlace:
    """Tests for PATCH /api/v1/projects/{project_id}/places/{place_id}."""

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_update_notes(self, mock_validate, client, sample_project):
        """Update a place's notes."""
        mock_validate.return_value = MOCK_ARTWORK
        project_id = sample_project["id"]

        # Add a place
        place_response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )
        place_id = place_response.json()["id"]

        # Update notes
        response = client.patch(
            f"/api/v1/projects/{project_id}/places/{place_id}",
            json={"notes": "Must visit this!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Must visit this!"

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_mark_as_visited(self, mock_validate, client, sample_project):
        """Mark a place as visited."""
        mock_validate.return_value = MOCK_ARTWORK
        project_id = sample_project["id"]

        # Add a place
        place_response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )
        place_id = place_response.json()["id"]

        # Mark as visited
        response = client.patch(
            f"/api/v1/projects/{project_id}/places/{place_id}",
            json={"visited": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["visited"] is True

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_project_auto_completed(self, mock_validate, client, sample_project):
        """Project should auto-complete when all places are visited."""
        mock_validate.return_value = MOCK_ARTWORK
        project_id = sample_project["id"]

        # Add a place
        place_response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )
        place_id = place_response.json()["id"]

        # Mark as visited
        client.patch(
            f"/api/v1/projects/{project_id}/places/{place_id}",
            json={"visited": True},
        )

        # Check project status
        project_response = client.get(f"/api/v1/projects/{project_id}")
        assert project_response.json()["status"] == "completed"

    @patch("app.services.place_service.ArticAPIClient.validate_artwork_exists")
    def test_cannot_delete_project_with_visited(self, mock_validate, client, sample_project):
        """Cannot delete a project with visited places."""
        mock_validate.return_value = MOCK_ARTWORK
        project_id = sample_project["id"]

        # Add and visit a place
        place_response = client.post(
            f"/api/v1/projects/{project_id}/places",
            json={"external_id": 129884},
        )
        place_id = place_response.json()["id"]
        client.patch(
            f"/api/v1/projects/{project_id}/places/{place_id}",
            json={"visited": True},
        )

        # Try to delete
        response = client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == 409
