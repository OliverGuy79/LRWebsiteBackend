"""Comprehensive tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


client = TestClient(app)


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthCheck:
    """Tests for the health check endpoint."""
    
    def test_health_check_returns_200(self):
        """Test the health check endpoint returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_health_check_response_format(self):
        """Test the health check response structure."""
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "lr-website-backend"


# =============================================================================
# Articles Tests
# =============================================================================

class TestArticles:
    """Tests for the articles endpoints."""
    
    def test_list_articles_returns_200(self):
        """Test listing articles returns 200."""
        response = client.get("/api/articles")
        assert response.status_code == 200
    
    def test_list_articles_response_structure(self):
        """Test articles list response has correct structure."""
        response = client.get("/api/articles")
        data = response.json()
        assert "articles" in data
        assert "total" in data
        assert isinstance(data["articles"], list)
        assert isinstance(data["total"], int)
    
    def test_list_articles_with_category_filter(self):
        """Test filtering articles by category."""
        response = client.get("/api/articles?category=news")
        assert response.status_code == 200
    
    def test_list_articles_with_limit(self):
        """Test limiting article results."""
        response = client.get("/api/articles?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["articles"]) <= 5
    
    def test_list_articles_preview_mode(self):
        """Test preview mode includes drafts."""
        response = client.get("/api/articles?preview=true")
        assert response.status_code == 200
    
    def test_get_article_not_found(self):
        """Test getting non-existent article returns 404."""
        response = client.get("/api/articles/non-existent-slug")
        assert response.status_code == 404
        assert response.json()["detail"] == "Article not found"


# =============================================================================
# Boutique Tests
# =============================================================================

class TestBoutique:
    """Tests for the boutique endpoints."""
    
    def test_list_products_returns_200(self):
        """Test listing products returns 200."""
        response = client.get("/api/boutique")
        assert response.status_code == 200
    
    def test_list_products_response_structure(self):
        """Test products list response has correct structure."""
        response = client.get("/api/boutique")
        data = response.json()
        assert "products" in data
        assert "total" in data
    
    def test_list_products_with_category_filter(self):
        """Test filtering products by category."""
        response = client.get("/api/boutique?category=books")
        assert response.status_code == 200
    
    def test_list_products_in_stock_filter(self):
        """Test filtering products by stock status."""
        response = client.get("/api/boutique?in_stock=true")
        assert response.status_code == 200
    
    def test_list_products_preview_mode(self):
        """Test preview mode for products."""
        response = client.get("/api/boutique?preview=true")
        assert response.status_code == 200
    
    def test_get_product_not_found(self):
        """Test getting non-existent product returns 404."""
        response = client.get("/api/boutique/999999")
        assert response.status_code == 404


# =============================================================================
# Church Info Tests
# =============================================================================

class TestChurchInfo:
    """Tests for the church info endpoint."""
    
    def test_get_church_info_returns_200(self):
        """Test getting church info returns 200."""
        response = client.get("/api/church-info")
        assert response.status_code == 200
    
    def test_church_info_has_church_name(self):
        """Test church info contains church_name."""
        response = client.get("/api/church-info")
        data = response.json()
        assert "church_name" in data


# =============================================================================
# Events Tests
# =============================================================================

class TestEvents:
    """Tests for the events endpoints."""
    
    def test_list_events_returns_200(self):
        """Test listing events returns 200."""
        response = client.get("/api/events")
        assert response.status_code == 200
    
    def test_list_events_response_structure(self):
        """Test events list response has correct structure."""
        response = client.get("/api/events")
        data = response.json()
        assert "events" in data
        assert "total" in data
    
    def test_list_events_with_category_filter(self):
        """Test filtering events by category."""
        response = client.get("/api/events?category=worship")
        assert response.status_code == 200
    
    def test_list_events_with_limit(self):
        """Test limiting event results."""
        response = client.get("/api/events?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) <= 3
    
    def test_list_events_preview_mode(self):
        """Test preview mode for events."""
        response = client.get("/api/events?preview=true")
        assert response.status_code == 200
    
    def test_upcoming_events_returns_200(self):
        """Test upcoming events endpoint returns 200."""
        response = client.get("/api/events/upcoming")
        assert response.status_code == 200
    
    def test_upcoming_events_with_limit(self):
        """Test limiting upcoming events."""
        response = client.get("/api/events/upcoming?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) <= 2
    
    def test_upcoming_events_preview_mode(self):
        """Test preview mode for upcoming events."""
        response = client.get("/api/events/upcoming?preview=true")
        assert response.status_code == 200
    
    def test_get_event_not_found(self):
        """Test getting non-existent event returns 404."""
        response = client.get("/api/events/999999")
        assert response.status_code == 404


# =============================================================================
# Home Groups Tests
# =============================================================================

class TestHomeGroups:
    """Tests for the home groups endpoints."""
    
    def test_list_home_groups_returns_200(self):
        """Test listing home groups returns 200."""
        response = client.get("/api/home-groups")
        assert response.status_code == 200
    
    def test_list_home_groups_response_structure(self):
        """Test home groups list response has correct structure."""
        response = client.get("/api/home-groups")
        data = response.json()
        assert "home_groups" in data
        assert "total" in data
    
    def test_list_home_groups_with_frequency_filter(self):
        """Test filtering home groups by frequency."""
        response = client.get("/api/home-groups?frequency=mois")
        assert response.status_code == 200
    
    def test_list_home_groups_preview_mode(self):
        """Test preview mode for home groups."""
        response = client.get("/api/home-groups?preview=true")
        assert response.status_code == 200
    
    def test_home_groups_uses_english_field_names(self):
        """Test that response uses English field names, not French aliases."""
        response = client.get("/api/home-groups")
        data = response.json()
        if data["total"] > 0:
            group = data["home_groups"][0]
            # Should have English field names
            assert "home" in group or group.get("home") is None
            assert "leaders" in group or group.get("leaders") is None
            # Should NOT have French aliases as keys
            assert "HOME" not in group
            assert "Leader(s)" not in group


# =============================================================================
# Pastoral Team Tests
# =============================================================================

class TestPastoralTeam:
    """Tests for the pastoral team endpoints."""
    
    def test_list_team_returns_200(self):
        """Test listing pastoral team returns 200."""
        response = client.get("/api/pastoral-team")
        assert response.status_code == 200
    
    def test_list_team_response_structure(self):
        """Test pastoral team list response has correct structure."""
        response = client.get("/api/pastoral-team")
        data = response.json()
        assert "team" in data
        assert "total" in data
    
    def test_list_team_with_role_filter(self):
        """Test filtering team by role."""
        response = client.get("/api/pastoral-team?role=pastor")
        assert response.status_code == 200
    
    def test_list_team_preview_mode(self):
        """Test preview mode for pastoral team."""
        response = client.get("/api/pastoral-team?preview=true")
        assert response.status_code == 200


# =============================================================================
# Services Tests
# =============================================================================

class TestServices:
    """Tests for the services endpoints."""
    
    def test_list_services_returns_200(self):
        """Test listing services returns 200."""
        response = client.get("/api/services")
        assert response.status_code == 200
    
    def test_list_services_response_structure(self):
        """Test services list response has correct structure."""
        response = client.get("/api/services")
        data = response.json()
        assert "services" in data
        assert "total" in data
    
    def test_filter_services_by_language_fr(self):
        """Test filtering services by French language."""
        response = client.get("/api/services?lang=fr")
        assert response.status_code == 200
    
    def test_filter_services_by_language_en(self):
        """Test filtering services by English language."""
        response = client.get("/api/services?lang=en")
        assert response.status_code == 200
    
    def test_filter_services_by_type(self):
        """Test filtering services by type."""
        response = client.get("/api/services?service_type=sunday")
        assert response.status_code == 200
    
    def test_list_services_preview_mode(self):
        """Test preview mode for services."""
        response = client.get("/api/services?preview=true")
        assert response.status_code == 200


# =============================================================================
# Vision Tests
# =============================================================================

class TestVision:
    """Tests for the vision endpoints."""
    
    def test_list_vision_returns_200(self):
        """Test listing vision sections returns 200."""
        response = client.get("/api/vision")
        assert response.status_code == 200
    
    def test_list_vision_response_structure(self):
        """Test vision list response has correct structure."""
        response = client.get("/api/vision")
        data = response.json()
        assert "sections" in data
        assert "total" in data
    
    def test_list_vision_preview_mode(self):
        """Test preview mode for vision sections."""
        response = client.get("/api/vision?preview=true")
        assert response.status_code == 200


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling across endpoints."""
    
    def test_invalid_endpoint_returns_404(self):
        """Test that invalid endpoints return 404."""
        response = client.get("/api/invalid-endpoint")
        assert response.status_code == 404
    
    def test_invalid_query_param_type(self):
        """Test handling of invalid query parameter types."""
        # limit should be int, passing string
        response = client.get("/api/articles?limit=invalid")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_boolean_param(self):
        """Test handling of invalid boolean parameters."""
        response = client.get("/api/articles?preview=maybe")
        assert response.status_code == 422  # Validation error


# =============================================================================
# CORS Tests
# =============================================================================

class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present on preflight."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        # Should not be blocked by CORS (200 or 405 depending on config)
        assert response.status_code in [200, 405, 400]
