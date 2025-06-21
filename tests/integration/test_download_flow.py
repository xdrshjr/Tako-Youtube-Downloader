"""
Integration tests for YouTube Downloader.

Tests the complete download flow with all components working together.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from youtube_downloader.core.validator import URLValidator
from youtube_downloader.core.downloader import VideoDownloader
from youtube_downloader.core.config import ConfigManager, DownloadConfig


class TestDownloadFlow:
    """Integration tests for the complete download workflow."""
    
    @pytest.fixture
    def temp_download_dir(self):
        """Create temporary download directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def test_config(self, temp_download_dir):
        """Create test configuration."""
        return DownloadConfig(
            quality="720p",
            format="mp4",
            output_directory=temp_download_dir,
            naming_pattern="{title}-{id}.{ext}",
            retry_attempts=1,
            timeout=10
        )
    
    def test_complete_download_workflow(self, test_config, temp_download_dir):
        """Test complete workflow from URL validation to download."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # Step 1: Validate URL
        validator = URLValidator()
        assert validator.validate_youtube_url(url)
        
        video_id = validator.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
        
        # Step 2: Configure downloader
        downloader = VideoDownloader(test_config)
        
        # Step 3: Mock the actual download to avoid network calls
        mock_video_info = {
            'id': 'dQw4w9WgXcQ',
            'title': 'Test Video',
            'duration': 212,
            'description': 'Test description',
            'uploader': 'Test Channel',
            'upload_date': '20090528',
            'view_count': 1000000,
            'like_count': 50000,
        }
        
        with patch('youtube_downloader.core.downloader.yt_dlp.YoutubeDL') as mock_yt_dlp:
            mock_ydl = Mock()
            mock_ydl.extract_info.return_value = mock_video_info
            mock_ydl.download.return_value = None
            mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
            
            # Step 4: Download video
            result = downloader.download_video(url)
            
            # Step 5: Verify results
            assert result.success is True
            assert result.video_info.video_id == "dQw4w9WgXcQ"
            assert result.video_info.title == "Test Video"
            assert result.error_message is None
    
    def test_workflow_with_invalid_url(self, test_config):
        """Test workflow with invalid URL."""
        invalid_url = "https://www.google.com"
        
        # Step 1: URL validation should fail
        validator = URLValidator()
        assert not validator.validate_youtube_url(invalid_url)
        
        # Step 2: Should raise error when trying to extract video ID
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            validator.extract_video_id(invalid_url)
    
    def test_workflow_error_handling(self, test_config):
        """Test error handling in workflow."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        downloader = VideoDownloader(test_config)
        
        # Mock download failure
        with patch('youtube_downloader.core.downloader.yt_dlp.YoutubeDL') as mock_yt_dlp:
            mock_ydl = Mock()
            mock_ydl.extract_info.side_effect = Exception("Network error")
            mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
            
            result = downloader.download_video(url)
            
            assert result.success is False
            assert "Network error" in result.error_message
            assert result.video_info is None 