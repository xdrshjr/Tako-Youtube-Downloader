"""
Tests for search-related API routes.
"""

import pytest
from unittest.mock import patch, Mock


class TestSearchRoutes:
    """Test cases for search-related API endpoints."""
    
    @patch('youtube_downloader.api.routes.search.search_service')
    def test_search_videos_success(self, mock_service, api_client):
        """Test successful video search."""
        # Mock the service response
        from youtube_downloader.api.models.responses import SearchResponse, SearchResultItem, StatusEnum
        from datetime import datetime
        
        mock_service.search_videos.return_value = SearchResponse(
            status=StatusEnum.SUCCESS,
            message="Found 2 videos",
            results=[
                SearchResultItem(
                    video_id="test1",
                    title="Test Video 1",
                    duration=300,
                    uploader="Test Channel 1",
                    upload_date="2024-01-01",
                    view_count=10000,
                    thumbnail_url="http://example.com/thumb1.jpg",
                    url="https://youtube.com/watch?v=test1"
                ),
                SearchResultItem(
                    video_id="test2",
                    title="Test Video 2",
                    duration=600,
                    uploader="Test Channel 2",
                    upload_date="2024-01-02",
                    view_count=20000,
                    thumbnail_url="http://example.com/thumb2.jpg",
                    url="https://youtube.com/watch?v=test2"
                )
            ],
            total_found=2,
            query="Python tutorial",
            timestamp=datetime.utcnow()
        )
        
        response = api_client.post(
            "/api/v1/search/videos",
            json={
                "query": "Python tutorial",
                "max_results": 10,
                "min_duration": 300,
                "max_duration": 1800
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_found"] == 2
        assert len(data["results"]) == 2
        assert data["query"] == "Python tutorial"
    
    def test_search_videos_missing_query(self, api_client):
        """Test search request without query."""
        response = api_client.post(
            "/api/v1/search/videos",
            json={"max_results": 10}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_search_videos_invalid_max_results(self, api_client):
        """Test search with invalid max_results."""
        # Test with negative value
        response = api_client.post(
            "/api/v1/search/videos",
            json={
                "query": "Python tutorial",
                "max_results": -1
            }
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with too large value
        response = api_client.post(
            "/api/v1/search/videos",
            json={
                "query": "Python tutorial",
                "max_results": 1000
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_search_videos_with_filters(self, api_client):
        """Test search with various filters."""
        response = api_client.post(
            "/api/v1/search/videos",
            json={
                "query": "Python tutorial",
                "max_results": 5,
                "sort_by": "view_count",
                "upload_date": "week",
                "min_duration": 600,
                "max_duration": 3600,
                "min_view_count": 1000,
                "exclude_shorts": True,
                "exclude_live": True
            }
        )
        
        # Should be successful (actual filtering happens in service layer)
        assert response.status_code == 200
    
    @patch('youtube_downloader.api.routes.search.search_service')
    def test_get_trending_videos(self, mock_service, api_client):
        """Test getting trending videos."""
        # Mock the service response
        from youtube_downloader.api.models.responses import SearchResponse, SearchResultItem, StatusEnum
        from datetime import datetime
        
        mock_service.get_trending_videos.return_value = SearchResponse(
            status=StatusEnum.SUCCESS,
            results=[
                SearchResultItem(
                    video_id="trend1",
                    title="Trending Video 1",
                    duration=300,
                    uploader="Trending Channel 1",
                    upload_date="2024-01-01",
                    view_count=10000,
                    thumbnail_url="http://example.com/thumb1.jpg",
                    url="https://youtube.com/watch?v=trend1"
                ),
                SearchResultItem(
                    video_id="trend2",
                    title="Trending Video 2",
                    duration=600,
                    uploader="Trending Channel 2",
                    upload_date="2024-01-02",
                    view_count=20000,
                    thumbnail_url="http://example.com/thumb2.jpg",
                    url="https://youtube.com/watch?v=trend2"
                )
            ],
            total_found=2,
            query="trending",
            timestamp=datetime.utcnow()
        )
        
        response = api_client.get("/api/v1/search/trending?max_results=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["results"]) == 2
    
    def test_get_trending_videos_invalid_max_results(self, api_client):
        """Test trending videos with invalid max_results."""
        response = api_client.get("/api/v1/search/trending?max_results=100")
        
        assert response.status_code == 422  # Validation error (max 50)
    
    @patch('youtube_downloader.api.services.search_service.SearchService')
    def test_get_recent_videos(self, mock_service, api_client):
        """Test getting recent videos."""
        # Mock the service response
        mock_service_instance = Mock()
        mock_service_instance.get_recent_videos.return_value = Mock(
            status="success",
            results=[Mock(title="Recent Video 1")],
            total_found=1,
            query="Python"
        )
        mock_service.return_value = mock_service_instance
        
        response = api_client.get("/api/v1/search/recent?query=Python&max_results=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_get_recent_videos_missing_query(self, api_client):
        """Test recent videos without query parameter."""
        response = api_client.get("/api/v1/search/recent")
        
        assert response.status_code == 422  # Validation error
    
    @patch('youtube_downloader.api.routes.search.search_service')
    def test_get_video_suggestions(self, mock_service, api_client):
        """Test getting video suggestions."""
        # Mock the service response
        mock_service.suggest_videos.return_value = [
            "Python Tutorial for Beginners",
            "Advanced Python Programming",
            "Python Web Development"
        ]
        
        response = api_client.get("/api/v1/search/suggestions?query=Python&max_results=3")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert "Python" in data[0]
    
    def test_get_suggestions_missing_query(self, api_client):
        """Test suggestions without query parameter."""
        response = api_client.get("/api/v1/search/suggestions")
        
        assert response.status_code == 422  # Validation error
    
    def test_get_suggestions_invalid_max_results(self, api_client):
        """Test suggestions with invalid max_results."""
        response = api_client.get("/api/v1/search/suggestions?query=Python&max_results=25")
        
        assert response.status_code == 422  # Validation error (max 20)
    
    @patch('youtube_downloader.api.routes.search.search_service')
    def test_search_service_error_handling(self, mock_service, api_client):
        """Test search service error handling."""
        # Mock the service to return an error
        from youtube_downloader.api.models.responses import SearchResponse, StatusEnum
        from datetime import datetime
        
        mock_service.search_videos.return_value = SearchResponse(
            status=StatusEnum.ERROR,
            message="Search failed: Network error",
            results=[],
            total_found=0,
            query="test",
            timestamp=datetime.utcnow()
        )
        
        response = api_client.post(
            "/api/v1/search/videos",
            json={"query": "test"}
        )
        
        assert response.status_code == 200  # Service errors return 200 with error status
        data = response.json()
        assert data["status"] == "error"
        assert "Search failed" in data["message"] 