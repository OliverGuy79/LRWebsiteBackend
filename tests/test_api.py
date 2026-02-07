"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "lr-website-backend"


def test_articles_list():
    """Test listing articles."""
    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data


def test_boutique_list():
    """Test listing products."""
    response = client.get("/api/boutique")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data


def test_church_info():
    """Test getting church info."""
    response = client.get("/api/church-info")
    assert response.status_code == 200
    data = response.json()
    assert "church_name" in data


def test_events_list():
    """Test listing events."""
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "total" in data


def test_events_upcoming():
    """Test listing upcoming events."""
    response = client.get("/api/events/upcoming")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "total" in data


def test_home_groups_list():
    """Test listing home groups."""
    response = client.get("/api/home-groups")
    assert response.status_code == 200
    data = response.json()
    assert "home_groups" in data
    assert "total" in data


def test_pastoral_team_list():
    """Test listing pastoral team."""
    response = client.get("/api/pastoral-team")
    assert response.status_code == 200
    data = response.json()
    assert "team" in data
    assert "total" in data


def test_services_list():
    """Test listing services."""
    response = client.get("/api/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "total" in data


def test_services_filter_language():
    """Test filtering services by language."""
    response = client.get("/api/services?lang=fr")
    assert response.status_code == 200


def test_vision_list():
    """Test listing vision sections."""
    response = client.get("/api/vision")
    assert response.status_code == 200
    data = response.json()
    assert "sections" in data
    assert "total" in data
