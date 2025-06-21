"""
Unit tests for search engine module.

This module tests the SearchEngine class that provides YouTube video search
functionality using yt-dlp.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from youtube_downloader.core.search_engine import (
    SearchEngine,
    SearchError,
    NetworkSearchError,
    YouTubeSearchError
)
from youtube_downloader.core.search_config import SearchConfig, FilterConfig
from youtube_downloader.core.video_filter import VideoSearchResult


class TestSearchEngine:
    """Test cases for SearchEngine class."""
    
    def create_mock_yt_dlp_result(self) -> dict:
        """Create mock yt-dlp search result."""
        return {
            'entries': [
                {
                    'id': 'video_1',
                    'title': 'Test Video 1',
                    'duration': 300,
                    'uploader': 'Test Channel 1',
                    'upload_date': '20240115',
                    'view_count': 10000,
                    'thumbnail': 'https://example.com/thumb1.jpg',
                    'description': 'Test description 1'
                },
                {
                    'id': 'video_2', 
                    'title': 'Test Video 2',
                    'duration': 600,
                    'uploader': 'Test Channel 2',
                    'upload_date': '20240110',
                    'view_count': 25000,
                    'thumbnail': 'https://example.com/thumb2.jpg',
                    'description': 'Test description 2'
                }
            ]
        }
    
    def test_search_engine_initialization(self):
        """Test SearchEngine initialization."""
        config = SearchConfig(search_query="test query")
        engine = SearchEngine(config)
        
        assert engine.config == config
        assert engine.config.search_query == "test query"
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_videos_success(self, mock_yt_dlp):
        """Test successful video search."""
        # Setup mock
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.create_mock_yt_dlp_result()
        
        # Test search
        config = SearchConfig(search_query="test query", max_results=2)
        engine = SearchEngine(config)
        results = engine.search_videos("test query", max_results=2)
        
        # Verify results
        assert len(results) == 2
        assert results[0].video_id == "video_1"
        assert results[0].title == "Test Video 1"
        assert results[0].duration == 300
        assert results[0].uploader == "Test Channel 1"
        assert results[0].upload_date == "2024-01-15"
        assert results[0].view_count == 10000
        
        assert results[1].video_id == "video_2"
        assert results[1].title == "Test Video 2"
        
        # Verify yt-dlp was called correctly
        mock_ydl.extract_info.assert_called_once()
        call_args = mock_ydl.extract_info.call_args[0]
        assert "ytsearch2:test query" in call_args[0]
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_videos_with_filters(self, mock_yt_dlp):
        """Test video search with filtering applied."""
        # Setup mock with mixed content
        mock_result = {
            'entries': [
                {
                    'id': 'short_video',
                    'title': 'Short Video',
                    'duration': 30,  # YouTube Short
                    'uploader': 'Channel A',
                    'upload_date': '20240115',
                    'view_count': 5000
                },
                {
                    'id': 'normal_video',
                    'title': 'Normal Video',
                    'duration': 300,
                    'uploader': 'Channel B',
                    'upload_date': '20240115',
                    'view_count': 15000
                }
            ]
        }
        
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = mock_result
        
        # Test search with filtering
        filter_config = FilterConfig(exclude_shorts=True, min_view_count=10000)
        config = SearchConfig(
            search_query="test",
            max_results=2,
            filter_config=filter_config
        )
        
        engine = SearchEngine(config)
        results = engine.search_videos("test", max_results=2)
        
        # Should filter out short video
        assert len(results) == 1
        assert results[0].video_id == "normal_video"
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_videos_network_error(self, mock_yt_dlp):
        """Test handling of network errors during search."""
        # Setup mock to raise network error
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Network error")
        
        config = SearchConfig()
        engine = SearchEngine(config)
        
        with pytest.raises(NetworkSearchError):
            engine.search_videos("test query")
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_videos_youtube_error(self, mock_yt_dlp):
        """Test handling of YouTube-specific errors."""
        # Setup mock to raise YouTube error
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("YouTube API error")
        
        config = SearchConfig()
        engine = SearchEngine(config)
        
        with pytest.raises(YouTubeSearchError):
            engine.search_videos("test query")
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_videos_empty_results(self, mock_yt_dlp):
        """Test handling of empty search results."""
        # Setup mock to return empty results
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {'entries': []}
        
        config = SearchConfig()
        engine = SearchEngine(config)
        results = engine.search_videos("nonexistent query")
        
        assert results == []
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_videos_missing_metadata(self, mock_yt_dlp):
        """Test handling of search results with missing metadata."""
        # Setup mock with incomplete metadata
        mock_result = {
            'entries': [
                {
                    'id': 'video_1',
                    'title': 'Complete Video',
                    'duration': 300,
                    'uploader': 'Channel',
                    'upload_date': '20240115',
                    'view_count': 10000
                },
                {
                    'id': 'video_2',
                    'title': 'Incomplete Video',
                    # Missing duration, uploader, etc.
                    'upload_date': '20240115'
                }
            ]
        }
        
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = mock_result
        
        config = SearchConfig()
        engine = SearchEngine(config)
        results = engine.search_videos("test")
        
        # Should only return videos with complete metadata
        assert len(results) == 1
        assert results[0].video_id == "video_1"
    
    def test_get_video_details_not_implemented(self):
        """Test get_video_details method (placeholder)."""
        config = SearchConfig()
        engine = SearchEngine(config)
        
        # This method is for future implementation
        with pytest.raises(NotImplementedError):
            engine.get_video_details(["video_id_1", "video_id_2"])
    
    def test_build_search_url(self):
        """Test search URL construction."""
        config = SearchConfig()
        engine = SearchEngine(config)
        
        # Test basic search URL
        url = engine._build_search_url("test query", 10)
        assert url == "ytsearch10:test query"
        
        # Test with special characters
        url = engine._build_search_url("python programming tutorial", 5)
        assert url == "ytsearch5:python programming tutorial"
    
    def test_parse_upload_date(self):
        """Test upload date parsing from yt-dlp format."""
        config = SearchConfig()
        engine = SearchEngine(config)
        
        # Test valid date
        parsed = engine._parse_upload_date("20240115")
        assert parsed == "2024-01-15"
        
        # Test invalid date
        parsed = engine._parse_upload_date("invalid")
        assert parsed == "1970-01-01"  # Default fallback
        
        # Test None
        parsed = engine._parse_upload_date(None)
        assert parsed == "1970-01-01"
    
    def test_validate_video_metadata(self):
        """Test video metadata validation."""
        config = SearchConfig()
        engine = SearchEngine(config)
        
        # Valid metadata
        valid_entry = {
            'id': 'test_id',
            'title': 'Test Title',
            'duration': 300,
            'uploader': 'Test Channel',
            'upload_date': '20240115',
            'view_count': 1000
        }
        assert engine._validate_video_metadata(valid_entry) is True
        
        # Missing required fields
        invalid_entry = {
            'id': 'test_id',
            'title': 'Test Title'
            # Missing duration, uploader, etc.
        }
        assert engine._validate_video_metadata(invalid_entry) is False
        
        # None values
        none_entry = {
            'id': 'test_id',
            'title': None,
            'duration': 300,
            'uploader': 'Channel',
            'upload_date': '20240115',
            'view_count': 1000
        }
        assert engine._validate_video_metadata(none_entry) is False


class TestSearchEngineIntegration:
    """Integration tests for SearchEngine with VideoFilter."""
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_and_filter_integration(self, mock_yt_dlp):
        """Test full search and filter integration."""
        # Setup mock with diverse content
        mock_result = {
            'entries': [
                {
                    'id': 'short_video',
                    'title': 'Short Video',
                    'duration': 30,
                    'uploader': 'Channel A',
                    'upload_date': '20240115',
                    'view_count': 1000
                },
                {
                    'id': 'medium_video',
                    'title': 'Medium Video',
                    'duration': 300,
                    'uploader': 'Channel B',
                    'upload_date': '20240115',
                    'view_count': 15000
                },
                {
                    'id': 'long_video',
                    'title': 'Long Video',
                    'duration': 1800,
                    'uploader': 'Channel C',
                    'upload_date': '20240115',
                    'view_count': 50000
                }
            ]
        }
        
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = mock_result
        
        # Configure search with filters
        filter_config = FilterConfig(
            min_duration=120,  # 2 minutes
            max_duration=900,  # 15 minutes
            exclude_shorts=True,
            min_view_count=10000
        )
        
        config = SearchConfig(
            search_query="tutorial",
            max_results=10,
            filter_config=filter_config
        )
        
        engine = SearchEngine(config)
        results = engine.search_videos("tutorial")
        
        # Should only return medium video that meets all criteria
        assert len(results) == 1
        assert results[0].video_id == "medium_video"
        assert results[0].duration == 300
        assert results[0].view_count == 15000


class TestSearchEngineConfiguration:
    """Test SearchEngine configuration handling."""
    
    def test_search_engine_with_different_sort_options(self):
        """Test SearchEngine with different sort configurations."""
        # Test relevance sort (default)
        config = SearchConfig(sort_by="relevance")
        engine = SearchEngine(config)
        assert engine.config.sort_by == "relevance"
        
        # Test upload date sort
        config = SearchConfig(sort_by="upload_date")
        engine = SearchEngine(config)
        assert engine.config.sort_by == "upload_date"
    
    def test_search_engine_with_upload_date_filters(self):
        """Test SearchEngine with upload date filtering."""
        config = SearchConfig(upload_date="week")
        engine = SearchEngine(config)
        assert engine.config.upload_date == "week"
    
    def test_search_engine_url_generation_edge_cases(self):
        """Test edge cases in search URL generation."""
        config = SearchConfig()
        engine = SearchEngine(config)
        
        # Empty query
        url = engine._build_search_url("", 10)
        assert url == "ytsearch10:"
        
        # Very long query
        long_query = "a" * 1000
        url = engine._build_search_url(long_query, 5)
        assert "ytsearch5:" in url
        assert long_query in url
        
        # Query with quotes
        query_with_quotes = 'python "tutorial" programming'
        url = engine._build_search_url(query_with_quotes, 10)
        assert query_with_quotes in url


class TestSearchEngineErrorHandling:
    """Test error handling in SearchEngine."""
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_engine_timeout_error(self, mock_yt_dlp):
        """Test handling of timeout errors."""
        import socket
        
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = socket.timeout("Connection timeout")
        
        config = SearchConfig()
        engine = SearchEngine(config)
        
        with pytest.raises(NetworkSearchError, match="timeout"):
            engine.search_videos("test query")
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_engine_permission_error(self, mock_yt_dlp):
        """Test handling of permission errors."""
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = PermissionError("Access denied")
        
        config = SearchConfig()
        engine = SearchEngine(config)
        
        with pytest.raises(YouTubeSearchError, match="Access denied"):
            engine.search_videos("test query")
    
    def test_search_engine_invalid_config(self):
        """Test SearchEngine with invalid configuration."""
        # This should be caught by SearchConfig validation
        with pytest.raises(ValueError):
            invalid_config = SearchConfig(max_results=-1)
            from youtube_downloader.core.search_config import SearchConfigManager
            manager = SearchConfigManager()
            manager.validate_config(invalid_config) 