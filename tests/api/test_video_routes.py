"""
Tests for video-related API routes.
"""

import pytest
from unittest.mock import patch, Mock


class TestVideoRoutes:
    """Test cases for video-related API endpoints."""
    
    def test_video_health_endpoint(self, api_client):
        """Test the video service health check."""
        response = api_client.get("/api/v1/video/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
    
    @patch('youtube_downloader.api.routes.video.download_service')
    def test_get_video_info_success(self, mock_service, api_client, sample_video_url):
        """Test successful video info retrieval."""
        # Mock the service response
        from youtube_downloader.api.models.responses import VideoInfoResponse, StatusEnum
        from datetime import datetime
        
        mock_service.get_video_info.return_value = VideoInfoResponse(
            status=StatusEnum.SUCCESS,
            message="Video information retrieved successfully",
            video_info={
                "video_id": "dQw4w9WgXcQ",
                "title": "Test Video",
                "uploader": "Test Channel",
                "duration": 212,
                "view_count": 1000000
            },
            timestamp=datetime.utcnow()
        )
        
        response = api_client.post(
            "/api/v1/video/info",
            json={"url": sample_video_url}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "video_info" in data
    
    def test_get_video_info_invalid_url(self, api_client):
        """Test video info with invalid URL."""
        response = api_client.post(
            "/api/v1/video/info",
            json={"url": "not-a-valid-url"}
        )
        
        # Should still return 200 but with error status
        assert response.status_code == 200
        # The actual validation happens in the service layer
    
    def test_get_video_info_missing_url(self, api_client):
        """Test video info request without URL."""
        response = api_client.post(
            "/api/v1/video/info",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('youtube_downloader.api.services.download_service.DownloadService')
    def test_download_video_success(self, mock_service, api_client, sample_video_url):
        """Test successful video download."""
        # Mock the service response
        mock_service_instance = Mock()
        mock_service_instance.download_video.return_value = Mock(
            status="success",
            message="Video downloaded successfully",
            task_id="test-task-id",
            output_path="/test/output.mp4",
            file_size=1024000
        )
        mock_service.return_value = mock_service_instance
        
        response = api_client.post(
            "/api/v1/video/download",
            json={
                "url": sample_video_url,
                "quality": "720p",
                "format": "mp4"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "task_id" in data
    
    @patch('youtube_downloader.api.routes.video.download_service')
    def test_download_video_with_error(self, mock_service, api_client, sample_video_url):
        """Test video download with error."""
        # Mock the service to return an error
        from youtube_downloader.api.models.responses import VideoDownloadResponse, StatusEnum
        from datetime import datetime
        
        mock_service.download_video.return_value = VideoDownloadResponse(
            status=StatusEnum.ERROR,
            message="Download failed: Invalid URL",
            timestamp=datetime.utcnow()
        )
        
        response = api_client.post(
            "/api/v1/video/download",
            json={"url": sample_video_url}
        )
        
        assert response.status_code == 400  # Should return 400 for error status
    
    def test_download_video_missing_url(self, api_client):
        """Test download request without URL."""
        response = api_client.post(
            "/api/v1/video/download",
            json={"quality": "720p"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_download_video_invalid_quality(self, api_client, sample_video_url):
        """Test download with invalid quality parameter."""
        response = api_client.post(
            "/api/v1/video/download",
            json={
                "url": sample_video_url,
                "quality": "invalid_quality"
            }
        )
        
        # Should accept any string (validation happens in service layer)
        # But might return error from service
        assert response.status_code in [200, 400]
    
    @patch('youtube_downloader.api.routes.video.download_service')
    def test_cancel_download_success(self, mock_service, api_client):
        """Test successful download cancellation."""
        # Mock the service response
        mock_service.cancel_download.return_value = {
            "status": "success",
            "message": "Download cancelled successfully"
        }
        
        response = api_client.delete("/api/v1/video/download/test-task-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('youtube_downloader.api.services.download_service.DownloadService')
    def test_cancel_download_not_found(self, mock_service, api_client):
        """Test cancelling non-existent download."""
        # Mock the service to return not found error
        mock_service_instance = Mock()
        mock_service_instance.cancel_download.return_value = {
            "status": "error",
            "message": "Download not found"
        }
        mock_service.return_value = mock_service_instance
        
        response = api_client.delete("/api/v1/video/download/nonexistent-id")
        
        assert response.status_code == 404
    
    @patch('youtube_downloader.api.routes.video.download_service')
    def test_get_active_downloads(self, mock_service, api_client):
        """Test getting list of active downloads."""
        # Mock the service response
        mock_service.get_active_downloads.return_value = {
            "active_downloads": ["task-1", "task-2"],
            "count": 2
        }
        
        response = api_client.get("/api/v1/video/downloads/active")
        
        assert response.status_code == 200
        data = response.json()
        assert "active_downloads" in data
        assert "count" in data
        assert data["count"] == 2 