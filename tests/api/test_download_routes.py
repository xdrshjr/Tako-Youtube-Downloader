"""
Tests for download-related API routes.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from youtube_downloader.api.main import app
from youtube_downloader.api.models.responses import DownloadStatusResponse, StatusEnum


@pytest.fixture
def api_client():
    """Create a test client for the API."""
    return TestClient(app)


class TestDownloadRoutes:
    """Test cases for download routes."""
    
    @patch('youtube_downloader.api.routes.download.download_service')
    def test_get_download_status_success(self, mock_service, api_client):
        """Test successful download status retrieval."""
        # Mock the service response
        mock_response = DownloadStatusResponse(
            status=StatusEnum.SUCCESS,
            message="Download status retrieved successfully",
            task_id="test-task-id",
            download_status=StatusEnum.COMPLETED,
            download_url="https://www.youtube.com/watch?v=test",
            video_title="Test Video",
            progress=100.0
        )
        mock_service.get_download_status.return_value = mock_response
        
        response = api_client.get("/api/v1/download/status/test-task-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["task_id"] == "test-task-id"
        assert data["download_status"] == "completed"
        
    @patch('youtube_downloader.api.routes.download.download_service')
    def test_get_download_status_not_found(self, mock_service, api_client):
        """Test download status for non-existent task."""
        # Mock the service response for not found
        mock_response = DownloadStatusResponse(
            status=StatusEnum.ERROR,
            message="Download task not-found-id not found",
            task_id="not-found-id",
            download_status=StatusEnum.ERROR
        )
        mock_service.get_download_status.return_value = mock_response
        
        response = api_client.get("/api/v1/download/status/not-found-id")
        
        assert response.status_code == 404
        
    @patch('youtube_downloader.api.routes.download.download_service')
    def test_get_download_status_in_progress(self, mock_service, api_client):
        """Test download status for in-progress download."""
        # Mock the service response for in-progress download
        mock_response = DownloadStatusResponse(
            status=StatusEnum.SUCCESS,
            message="Download status retrieved successfully",
            task_id="progress-task-id",
            download_status=StatusEnum.IN_PROGRESS,
            download_url="https://www.youtube.com/watch?v=test",
            video_title="Test Video",
            progress=45.5
        )
        mock_service.get_download_status.return_value = mock_response
        
        response = api_client.get("/api/v1/download/status/progress-task-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["download_status"] == "in_progress"
        assert data["progress"] == 45.5 