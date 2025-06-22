"""
Tests for the download service.
"""

import pytest
from unittest.mock import Mock, patch
from youtube_downloader.api.services.download_service import DownloadService
from youtube_downloader.api.models.requests import VideoDownloadRequest, VideoInfoRequest


class TestDownloadService:
    """Test cases for the DownloadService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Service will be created in individual tests with proper mocks
        pass
    
    @patch('youtube_downloader.api.services.download_service.VideoDownloader')
    @patch('youtube_downloader.api.services.download_service.URLValidator')
    @patch('youtube_downloader.api.services.download_service.ConfigManager')
    def test_get_video_info_success(self, mock_config_manager_class, mock_validator_class, mock_downloader_class):
        """Test successful video info retrieval."""
        # Mock config manager
        mock_config_manager = Mock()
        mock_config_manager.get_config.return_value = Mock()
        mock_config_manager_class.return_value = mock_config_manager

        # Mock validator
        mock_validator = Mock()
        mock_validator.validate_youtube_url.return_value = True
        mock_validator.extract_video_id.return_value = "test_video_id"
        mock_validator_class.return_value = mock_validator

        # Mock downloader
        mock_downloader = Mock()
        mock_video_info = Mock()
        mock_video_info.title = "Test Video"
        mock_video_info.uploader = "Test Channel"
        mock_video_info.duration = 300
        mock_video_info.upload_date = "20231201"
        mock_video_info.view_count = 1000000
        mock_video_info.like_count = 50000
        mock_video_info.description = "Test description"
        mock_video_info.thumbnail_url = "https://test.com/thumb.jpg"

        mock_downloader.get_video_info.return_value = mock_video_info
        mock_downloader_class.return_value = mock_downloader

        # Create service after mocks are set up
        service = DownloadService()

        # Test
        request = VideoInfoRequest(url="https://www.youtube.com/watch?v=test_id")
        response = service.get_video_info(request)
        
        # Assertions
        assert response.status == "success"
        assert response.message == "Video information retrieved successfully"
        assert response.video_info is not None
        assert response.video_info["title"] == "Test Video"
        assert response.video_info["uploader"] == "Test Channel"
        assert response.video_info["video_id"] == "test_video_id"
    
    @patch('youtube_downloader.api.services.download_service.URLValidator')
    @patch('youtube_downloader.api.services.download_service.ConfigManager')
    def test_get_video_info_invalid_url(self, mock_config_manager_class, mock_validator_class):
        """Test video info with invalid URL."""
        # Mock config manager
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        
        # Mock validator to return False
        mock_validator = Mock()
        mock_validator.validate_youtube_url.return_value = False
        mock_validator_class.return_value = mock_validator
        
        # Create service after mocks are set up
        service = DownloadService()
        
        # Test
        request = VideoInfoRequest(url="invalid_url")
        response = service.get_video_info(request)
        
        # Assertions
        assert response.status == "error"
        assert response.message == "Invalid YouTube URL"
        assert response.video_info is None
    
    @patch('youtube_downloader.api.services.download_service.Path')
    @patch('youtube_downloader.api.services.download_service.VideoDownloader')
    @patch('youtube_downloader.api.services.download_service.URLValidator')
    @patch('youtube_downloader.api.services.download_service.ConfigManager')
    def test_download_video_success(self, mock_config_manager_class, mock_validator_class, mock_downloader_class, mock_path):
        """Test successful video download."""
        # Mock config manager
        mock_config_manager = Mock() 
        mock_config_manager.get_config.return_value = Mock()
        mock_config_manager_class.return_value = mock_config_manager

        # Mock validator
        mock_validator = Mock()
        mock_validator.validate_youtube_url.return_value = True
        mock_validator_class.return_value = mock_validator
        
        # Mock Path
        mock_path.return_value.mkdir = Mock()
        
        # Mock downloader
        mock_downloader = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_path = "/test/output.mp4"
        mock_result.file_size = 1024000
        mock_result.error_message = None
        
        mock_downloader.download_video.return_value = mock_result
        mock_downloader_class.return_value = mock_downloader

        # Create service after mocks are set up
        service = DownloadService()

        # Test
        request = VideoDownloadRequest(
            url="https://www.youtube.com/watch?v=test_id",
            quality="720p",
            format="mp4"
        )
        response = service.download_video(request)
        
        # Assertions
        assert response.status == "success"
        assert response.message == "Video downloaded successfully"
        assert response.output_path == "/test/output.mp4"
        assert response.file_size == 1024000
        assert response.task_id is not None
    
    @patch('youtube_downloader.api.services.download_service.URLValidator')
    @patch('youtube_downloader.api.services.download_service.ConfigManager')
    def test_download_video_invalid_url(self, mock_config_manager_class, mock_validator_class):
        """Test video download with invalid URL."""
        # Mock config manager
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        
        # Mock validator to return False
        mock_validator = Mock()
        mock_validator.validate_youtube_url.return_value = False
        mock_validator_class.return_value = mock_validator
        
        # Create service after mocks are set up
        service = DownloadService()
        
        # Test
        request = VideoDownloadRequest(url="invalid_url")
        response = service.download_video(request)
        
        # Assertions
        assert response.status == "error"
        assert response.message == "Invalid YouTube URL"
    
    @patch('youtube_downloader.api.services.download_service.Path')
    @patch('youtube_downloader.api.services.download_service.VideoDownloader')
    @patch('youtube_downloader.api.services.download_service.URLValidator')
    @patch('youtube_downloader.api.services.download_service.ConfigManager')
    def test_download_video_failure(self, mock_config_manager_class, mock_validator_class, mock_downloader_class, mock_path):
        """Test video download failure."""
        # Mock config manager
        mock_config_manager = Mock()
        mock_config_manager.get_config.return_value = Mock()
        mock_config_manager_class.return_value = mock_config_manager

        # Mock validator
        mock_validator = Mock()
        mock_validator.validate_youtube_url.return_value = True
        mock_validator_class.return_value = mock_validator
        
        # Mock Path
        mock_path.return_value.mkdir = Mock()
        
        # Mock downloader to return failure
        mock_downloader = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_message = "Download failed: Network error"
        
        mock_downloader.download_video.return_value = mock_result
        mock_downloader_class.return_value = mock_downloader

        # Create service after mocks are set up
        service = DownloadService()

        # Test
        request = VideoDownloadRequest(url="https://www.youtube.com/watch?v=test_id")
        response = service.download_video(request)
        
        # Assertions
        assert response.status == "error"
        assert "Download failed" in response.message or "Invalid YouTube URL" in response.message
    
    def test_cancel_download_success(self):
        """Test successful download cancellation."""
        service = DownloadService()
        
        # Add a mock download to active downloads
        mock_downloader = Mock()
        task_id = "test_task_id"
        service.active_downloads[task_id] = mock_downloader
        
        # Test
        result = service.cancel_download(task_id)
        
        # Assertions
        assert result["status"] == "success"
        assert task_id not in service.active_downloads
        mock_downloader.cancel_download.assert_called_once()
    
    def test_cancel_download_not_found(self):
        """Test cancelling non-existent download."""
        service = DownloadService()
        
        # Test
        result = service.cancel_download("nonexistent_id")
        
        # Assertions
        assert result["status"] == "error"
        assert "not found" in result["message"]
    
    def test_get_active_downloads(self):
        """Test getting active downloads."""
        service = DownloadService()
        
        # Add some mock downloads
        service.active_downloads["task1"] = Mock()
        service.active_downloads["task2"] = Mock()
        
        # Test
        result = service.get_active_downloads()
        
        # Assertions
        assert result["count"] == 2
        assert "task1" in result["active_downloads"]
        assert "task2" in result["active_downloads"] 