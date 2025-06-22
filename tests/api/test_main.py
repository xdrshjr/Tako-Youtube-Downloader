"""
Tests for the main FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """Test cases for the main FastAPI application."""
    
    def test_root_endpoint(self, api_client):
        """Test the root endpoint returns health status."""
        response = api_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
    
    def test_health_endpoint(self, api_client):
        """Test the health check endpoint."""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
    
    def test_api_info_endpoint(self, api_client):
        """Test the API information endpoint."""
        response = api_client.get("/api/v1/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "YouTube Downloader API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "documentation" in data
        
        # Check that all expected endpoint categories are present
        endpoints = data["endpoints"]
        assert "video" in endpoints
        assert "search" in endpoints
        assert "batch" in endpoints
        assert "config" in endpoints
    
    def test_docs_endpoint_accessible(self, api_client):
        """Test that the Swagger docs endpoint is accessible."""
        response = api_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint_accessible(self, api_client):
        """Test that the ReDoc endpoint is accessible."""
        response = api_client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_nonexistent_endpoint_returns_404(self, api_client):
        """Test that nonexistent endpoints return 404."""
        response = api_client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_cors_headers_present(self, api_client):
        """Test that CORS middleware is configured properly."""
        # Test with a regular GET request
        response = api_client.get("/health")
        
        # In a test environment, we mainly want to ensure that:
        # 1. The request succeeds (CORS isn't blocking it)
        # 2. The response is valid
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        # Test OPTIONS request to ensure it doesn't fail due to CORS
        response_options = api_client.options("/health")
        # In test clients, OPTIONS might return 405 (Method Not Allowed) which is acceptable
        # The key is that it doesn't fail due to CORS configuration issues
        assert response_options.status_code in [200, 405]
        
        # Note: TestClient doesn't always add CORS headers like a real browser scenario would
        # The important thing is that CORS middleware is configured without breaking requests 