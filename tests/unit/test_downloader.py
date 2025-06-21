"""
Unit tests for VideoDownloader class.

Tests the video downloading functionality with mocked yt-dlp calls.
"""

import pytest
from unittest.mock import Mock, patch, call
from pathlib import Path
from youtube_downloader.core.downloader import VideoDownloader, DownloadResult, VideoInfo
from youtube_downloader.core.config import DownloadConfig


class TestVideoDownloader:
    """Test cases for VideoDownloader class."""
    
    @pytest.fixture
    def download_config(self):
        """Create a test download configuration."""
        return DownloadConfig(
            quality="720p",
            format="mp4",
            audio_format="mp3",
            output_directory="./test_downloads",
            naming_pattern="{title}-{id}.{ext}",
            create_subdirs=False,
            concurrent_downloads=1,
            retry_attempts=3,
            timeout=30,
            rate_limit=None
        )
    
    @pytest.fixture
    def downloader(self, download_config):
        """Create VideoDownloader instance for testing."""
        return VideoDownloader(download_config)
    
    @pytest.fixture
    def mock_video_info(self):
        """Create mock video information."""
        return {
            'id': 'dQw4w9WgXcQ',
            'title': 'Test Video Title',
            'duration': 212,
            'description': 'Test video description',
            'uploader': 'Test Channel',
            'upload_date': '20090528',
            'view_count': 1000000,
            'like_count': 50000,
            'formats': [
                {
                    'format_id': '720p',
                    'height': 720,
                    'width': 1280,
                    'ext': 'mp4',
                    'filesize': 50000000
                }
            ]
        }
    
    @patch('youtube_downloader.core.downloader.yt_dlp.YoutubeDL')
    def test_get_video_info_success(self, mock_yt_dlp, downloader, mock_video_info):
        """Test successful video information retrieval."""
        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_video_info
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = downloader.get_video_info(url)
        
        assert isinstance(result, VideoInfo)
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.title == "Test Video Title"
        assert result.duration == 212
        assert result.uploader == "Test Channel"
        
        mock_ydl.extract_info.assert_called_once_with(url, download=False)
    
    @patch('youtube_downloader.core.downloader.yt_dlp.YoutubeDL')
    def test_get_video_info_error(self, mock_yt_dlp, downloader):
        """Test video information retrieval with error."""
        mock_ydl = Mock()
        mock_ydl.extract_info.side_effect = Exception("Video not available")
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=invalidid"
        
        with pytest.raises(Exception, match="Video not available"):
            downloader.get_video_info(url)
    
    @patch('youtube_downloader.core.downloader.yt_dlp.YoutubeDL')
    def test_download_video_success(self, mock_yt_dlp, downloader, mock_video_info):
        """Test successful video download."""
        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_video_info
        mock_ydl.download.return_value = None
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = downloader.download_video(url)
        
        assert isinstance(result, DownloadResult)
        assert result.success is True
        assert result.video_info.video_id == "dQw4w9WgXcQ"
        assert result.error_message is None
        assert result.output_path is not None
        
        mock_ydl.download.assert_called_once_with([url])
    
    @patch('youtube_downloader.core.downloader.yt_dlp.YoutubeDL')
    def test_download_video_failure(self, mock_yt_dlp, downloader):
        """Test video download failure."""
        mock_ydl = Mock()
        mock_ydl.extract_info.side_effect = Exception("Download failed")
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=invalidid"
        result = downloader.download_video(url)
        
        assert isinstance(result, DownloadResult)
        assert result.success is False
        assert result.error_message == "Download failed"
        assert result.video_info is None
        assert result.output_path is None
    
    def test_download_config_application(self, download_config):
        """Test that download configuration is properly applied."""
        downloader = VideoDownloader(download_config)
        
        # Test that config values are properly set
        assert downloader.config.quality == "720p"
        assert downloader.config.format == "mp4"
        assert downloader.config.output_directory == "./test_downloads"
    
    @patch('youtube_downloader.core.downloader.yt_dlp.YoutubeDL')
    def test_yt_dlp_options_configuration(self, mock_yt_dlp, downloader, mock_video_info):
        """Test that yt-dlp options are configured correctly."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # Mock to allow info extraction but prevent actual download
        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_video_info
        mock_ydl.download.side_effect = Exception("Test exception")
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        
        try:
            downloader.download_video(url)
        except:
            pass
        
        # Verify yt-dlp was called multiple times (info + download)
        assert mock_yt_dlp.call_count >= 2
        
        # Check the download call (last call) for outtmpl
        last_call_args = mock_yt_dlp.call_args[0][0]  # Get the options dict from last call
        
        assert 'outtmpl' in last_call_args
        assert last_call_args['format'] == 'best[height<=720]'
        assert last_call_args['extract_flat'] is False
    
    def test_cancel_download(self, downloader):
        """Test download cancellation functionality."""
        # Initially not cancelled
        assert not downloader.is_cancelled
        
        # Cancel download
        downloader.cancel_download()
        assert downloader.is_cancelled
        
        # Reset cancellation
        downloader.reset_cancellation()
        assert not downloader.is_cancelled
    
    def test_progress_callback(self, downloader):
        """Test progress callback functionality."""
        progress_data = {
            'status': 'downloading',
            'downloaded_bytes': 1024000,
            'total_bytes': 10240000,
            'speed': 512000,
            'eta': 18
        }
        
        # Mock progress callback
        callback_mock = Mock()
        downloader.set_progress_callback(callback_mock)
        
        # Simulate progress update
        downloader._progress_hook(progress_data)
        
        callback_mock.assert_called_once_with(progress_data) 