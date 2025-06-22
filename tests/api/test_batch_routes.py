"""
Tests for batch download-related API routes.
"""

import pytest
from unittest.mock import patch, Mock


class TestBatchRoutes:
    """Test cases for batch download-related API endpoints."""
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_start_batch_download_success(self, mock_service, api_client):
        """Test successful batch download start."""
        from youtube_downloader.api.models.responses import BatchDownloadResponse, StatusEnum
        from datetime import datetime
        
        mock_service.start_batch_download.return_value = BatchDownloadResponse(
            status=StatusEnum.SUCCESS,
            message="Batch download started with 2 videos",
            task_id="batch-test-id",
            total_videos=2,
            tasks=[],
            timestamp=datetime.utcnow()
        )
        
        response = api_client.post(
            "/api/v1/batch/download",
            json={
                "urls": [
                    "https://www.youtube.com/watch?v=test1",
                    "https://www.youtube.com/watch?v=test2"
                ],
                "quality": "720p",
                "format": "mp4"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["task_id"] == "batch-test-id"
        assert data["total_videos"] == 2
    
    def test_start_batch_download_missing_urls(self, api_client):
        """Test batch download without URLs."""
        response = api_client.post(
            "/api/v1/batch/download",
            json={"quality": "720p"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_start_batch_download_empty_urls(self, api_client):
        """Test batch download with empty URL list."""
        response = api_client.post(
            "/api/v1/batch/download",
            json={"urls": []}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_start_batch_download_invalid_concurrent_downloads(self, api_client):
        """Test batch download with invalid concurrent downloads."""
        # Test with value too high
        response = api_client.post(
            "/api/v1/batch/download",
            json={
                "urls": ["https://www.youtube.com/watch?v=test1"],
                "max_concurrent_downloads": 15  # Max is 10
            }
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with zero value
        response = api_client.post(
            "/api/v1/batch/download",
            json={
                "urls": ["https://www.youtube.com/watch?v=test1"],
                "max_concurrent_downloads": 0
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_start_batch_download_service_error(self, mock_service, api_client):
        """Test batch download with service error."""
        # Mock the service to return an error
        from youtube_downloader.api.models.responses import BatchDownloadResponse, StatusEnum
        from datetime import datetime
        
        mock_service.start_batch_download.return_value = BatchDownloadResponse(
            status=StatusEnum.ERROR,
            message="Failed to start batch download",
            task_id="",
            total_videos=0,
            tasks=[],
            timestamp=datetime.utcnow()
        )
        
        response = api_client.post(
            "/api/v1/batch/download",
            json={
                "urls": ["https://www.youtube.com/watch?v=test1"]
            }
        )
        
        assert response.status_code == 400  # Service error returns 400
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_get_batch_progress_success(self, mock_service, api_client):
        """Test successful batch progress retrieval."""
        from youtube_downloader.api.models.responses import BatchProgressResponse, StatusEnum
        from datetime import datetime
        
        mock_service.get_batch_progress.return_value = BatchProgressResponse(
            status=StatusEnum.IN_PROGRESS,
            message="Batch progress: 50.0%",
            task_id="batch-test-id",
            overall_progress=50.0,
            total_videos=2,
            completed_videos=1,
            failed_videos=0,
            active_downloads=1,
            tasks=[],
            timestamp=datetime.utcnow()
        )
        
        response = api_client.get("/api/v1/batch/progress/batch-test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["overall_progress"] == 50.0
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_get_batch_progress_not_found(self, mock_service, api_client):
        """Test batch progress for non-existent task."""
        # Mock the service to return not found
        from youtube_downloader.api.models.responses import BatchProgressResponse, StatusEnum
        from datetime import datetime
        
        mock_service.get_batch_progress.return_value = BatchProgressResponse(
            status=StatusEnum.ERROR,
            message="Batch download not found",
            task_id="nonexistent-id",
            overall_progress=0.0,
            total_videos=0,
            completed_videos=0,
            failed_videos=0,
            active_downloads=0,
            tasks=[],
            timestamp=datetime.utcnow()
        )
        
        response = api_client.get("/api/v1/batch/progress/nonexistent-id")
        
        assert response.status_code == 404
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_cancel_batch_download_success(self, mock_service, api_client):
        """Test successful batch download cancellation."""
        # Mock the service response
        mock_service.cancel_batch_download.return_value = {
            "status": "success",
            "message": "Batch download cancelled successfully"
        }
        
        response = api_client.delete("/api/v1/batch/download/batch-test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "cancelled" in data["message"]
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_cancel_batch_download_not_found(self, mock_service, api_client):
        """Test cancelling non-existent batch download."""
        # Mock the service to return not found error
        mock_service.cancel_batch_download.return_value = {
            "status": "error",
            "message": "Batch download not found"
        }
        
        response = api_client.delete("/api/v1/batch/download/nonexistent-id")
        
        assert response.status_code == 404
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_cancel_batch_download_other_error(self, mock_service, api_client):
        """Test cancelling batch download with other error."""
        # Mock the service to return other error
        mock_service.cancel_batch_download.return_value = {
            "status": "error",
            "message": "Cannot cancel already completed batch"
        }
        
        response = api_client.delete("/api/v1/batch/download/completed-id")
        
        assert response.status_code == 400
    
    @patch('youtube_downloader.api.routes.batch.batch_service')
    def test_get_active_batches(self, mock_service, api_client):
        """Test getting list of active batch downloads."""
        # Mock the service response
        mock_service.get_active_batches.return_value = {
            "active_batches": {
                "batch-1": {
                    "status": "downloading",
                    "progress": 25.0,
                    "total_videos": 4,
                    "completed": 1,
                    "failed": 0,
                    "active": 1
                },
                "batch-2": {
                    "status": "downloading",
                    "progress": 75.0,
                    "total_videos": 2,
                    "completed": 1,
                    "failed": 0,
                    "active": 1
                }
            },
            "count": 2
        }
        
        response = api_client.get("/api/v1/batch/active")
        
        assert response.status_code == 200
        data = response.json()
        assert "active_batches" in data
        assert "count" in data
        assert data["count"] == 2
        assert "batch-1" in data["active_batches"]
        assert "batch-2" in data["active_batches"]
    
    def test_batch_download_with_all_optional_params(self, api_client):
        """Test batch download with all optional parameters."""
        response = api_client.post(
            "/api/v1/batch/download",
            json={
                "urls": [
                    "https://www.youtube.com/watch?v=test1",
                    "https://www.youtube.com/watch?v=test2"
                ],
                "quality": "1080p",
                "format": "webm",
                "output_directory": "./custom_downloads",
                "audio_format": "aac",
                "max_concurrent_downloads": 5,
                "retry_failed_downloads": False
            }
        )
        
        # Should be successful (service handles the actual processing)
        assert response.status_code == 200 