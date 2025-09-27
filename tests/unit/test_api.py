"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from social_trends_harvester.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "providers" in data


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Social Trends Harvester"
        assert "version" in data
        assert "endpoints" in data


class TestTrendingEndpoint:
    """Test trending endpoint."""

    def test_trending_mock_provider(self, client):
        """Test trending endpoint with mock provider."""
        response = client.get("/trending?provider=mock&count=5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "provider" in data
        assert data["provider"] == "mock"
        assert len(data["items"]) <= 5

    def test_trending_invalid_count(self, client):
        """Test trending endpoint with invalid count."""
        response = client.get("/trending?provider=mock&count=0")
        assert response.status_code == 400

    def test_trending_invalid_provider(self, client):
        """Test trending endpoint with invalid provider."""
        response = client.get("/trending?provider=nonexistent&count=5")
        assert response.status_code == 400


class TestHashtagEndpoint:
    """Test hashtag endpoint."""

    def test_hashtag_mock_provider(self, client):
        """Test hashtag endpoint with mock provider."""
        response = client.get("/hashtag/trending?provider=mock&count=3")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "hashtag" in data
        assert data["hashtag"] == "trending"
        assert data["provider"] == "mock"
        assert len(data["items"]) <= 3


class TestProvidersEndpoint:
    """Test providers endpoint."""

    def test_providers_list(self, client):
        """Test providers endpoint returns available providers."""
        response = client.get("/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check first provider has required fields
        provider = data[0]
        assert "name" in provider
        assert "supported_regions" in provider
        assert "supported_features" in provider


class TestComplianceEndpoint:
    """Test compliance endpoint."""

    def test_compliance_info(self, client):
        """Test compliance endpoint returns compliance info."""
        response = client.get("/compliance")
        assert response.status_code == 200
        data = response.json()
        assert "robots_txt_respected" in data
        assert "rate_limiting_enabled" in data
        assert "user_agent" in data
        assert data["robots_txt_respected"] is True
        assert data["rate_limiting_enabled"] is True
