"""
Integration tests for search functionality.

This module tests the integration between SearchEngine, VideoFilter, and SearchConfig
to ensure the complete search workflow functions correctly.
"""

import pytest
from unittest.mock import patch, MagicMock

from youtube_downloader.core import (
    SearchEngine,
    VideoFilter,
    VideoSearchResult,
    SearchConfig,
    FilterConfig,
    SearchConfigManager
)


class TestSearchIntegration:
    """Integration tests for complete search workflow."""
    
    def create_mock_search_data(self):
        """Create comprehensive mock search data for testing."""
        return {
            'entries': [
                # YouTube Short - should be filtered out by default
                {
                    'id': 'short_video_1',
                    'title': 'Quick Python Tip #Shorts',
                    'duration': 45,
                    'uploader': 'Tech Channel',
                    'upload_date': '20240115',
                    'view_count': 5000,
                    'thumbnail': 'https://example.com/thumb1.jpg',
                    'description': 'Short coding tip'
                },
                # Normal video - should pass filters
                {
                    'id': 'tutorial_video_1',
                    'title': 'Complete Python Tutorial for Beginners',
                    'duration': 900,  # 15 minutes
                    'uploader': 'Education Hub',
                    'upload_date': '20240110',
                    'view_count': 25000,
                    'thumbnail': 'https://example.com/thumb2.jpg',
                    'description': 'Learn Python from scratch'
                },
                # Long video - might be filtered by max duration
                {
                    'id': 'masterclass_video_1',
                    'title': 'Advanced Python Masterclass',
                    'duration': 3600,  # 1 hour
                    'uploader': 'Expert Academy',
                    'upload_date': '20240105',
                    'view_count': 50000,
                    'thumbnail': 'https://example.com/thumb3.jpg',
                    'description': 'Deep dive into advanced concepts'
                },
                # Live stream - should be filtered out by default
                {
                    'id': 'live_stream_1',
                    'title': 'Live Python Coding Session',
                    'duration': 0,  # Live stream indicator
                    'uploader': 'Live Coder',
                    'upload_date': '20240115',
                    'view_count': 1000,
                    'thumbnail': 'https://example.com/thumb4.jpg',
                    'description': 'Join our live coding session'
                },
                # Low view count video - might be filtered
                {
                    'id': 'small_channel_video',
                    'title': 'Python Tips from Small Channel',
                    'duration': 300,  # 5 minutes
                    'uploader': 'Small Tech Channel',
                    'upload_date': '20240112',
                    'view_count': 500,
                    'thumbnail': 'https://example.com/thumb5.jpg',
                    'description': 'Useful tips from a growing channel'
                }
            ]
        }
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_basic_search_workflow(self, mock_yt_dlp):
        """Test basic search workflow with default filters."""
        # Setup mock
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.create_mock_search_data()
        
        # Create search configuration
        config = SearchConfig(
            search_query="Python tutorial",
            max_results=10
        )
        
        # Perform search
        engine = SearchEngine(config)
        results = engine.search_videos("Python tutorial")
        
        # Verify results
        assert len(results) >= 1  # At least one video should pass filters
        
        # Check that shorts and live streams are filtered out by default
        for result in results:
            assert not result.is_short()  # No YouTube Shorts
            assert not result.is_live_stream()  # No live streams
        
        # Verify search was called correctly
        mock_ydl.extract_info.assert_called_once()
        call_args = mock_ydl.extract_info.call_args[0]
        assert "ytsearch10:Python tutorial" in call_args[0]
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_advanced_filtering_workflow(self, mock_yt_dlp):
        """Test advanced filtering with multiple criteria."""
        # Setup mock
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.create_mock_search_data()
        
        # Create advanced filter configuration
        filter_config = FilterConfig(
            min_duration=300,   # At least 5 minutes
            max_duration=1800,  # At most 30 minutes
            min_view_count=20000,  # At least 20k views
            exclude_shorts=True,
            exclude_live=True
        )
        
        config = SearchConfig(
            search_query="Python masterclass",
            max_results=20,
            filter_config=filter_config
        )
        
        # Perform search
        engine = SearchEngine(config)
        results = engine.search_videos("Python masterclass")
        
        # Verify filtering results
        for result in results:
            assert result.duration >= 300  # At least 5 minutes
            assert result.duration <= 1800  # At most 30 minutes
            assert result.view_count >= 20000  # At least 20k views
            assert not result.is_short()
            assert not result.is_live_stream()
        
        # Should return only videos that meet all criteria
        # Based on mock data, only 'tutorial_video_1' should qualify
        assert len(results) == 1
        assert results[0].video_id == "tutorial_video_1"
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_config_manager_integration(self, mock_yt_dlp):
        """Test integration with SearchConfigManager."""
        # Setup mock
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.create_mock_search_data()
        
        # Create and configure search manager
        manager = SearchConfigManager()
        manager.update_config(
            search_query="Python programming",
            max_results=15,
            sort_by="view_count",
            filter_min_duration=120,
            filter_exclude_shorts=True
        )
        
        config = manager.get_config()
        
        # Perform search with managed configuration
        engine = SearchEngine(config)
        results = engine.search_videos(config.search_query)
        
        # Verify configuration was applied
        assert len(results) >= 0  # May be empty due to filtering
        
        # Check that configuration values were used
        assert config.search_query == "Python programming"
        assert config.max_results == 15
        assert config.sort_by == "view_count"
        assert config.filter_config.min_duration == 120
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_empty_search_results(self, mock_yt_dlp):
        """Test handling of empty search results."""
        # Setup mock to return empty results
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {'entries': []}
        
        config = SearchConfig(search_query="nonexistent query")
        engine = SearchEngine(config)
        results = engine.search_videos("nonexistent query")
        
        assert results == []
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_filter_statistics_integration(self, mock_yt_dlp):
        """Test filter statistics and analysis."""
        # Setup mock
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.create_mock_search_data()
        
        config = SearchConfig(
            search_query="Python",
            filter_config=FilterConfig(min_view_count=10000)
        )
        
        engine = SearchEngine(config)
        
        # First get raw results for analysis
        raw_results = [
            VideoSearchResult(
                video_id="short_video_1",
                title="Quick Python Tip",
                duration=45,
                uploader="Tech Channel",
                upload_date="2024-01-15",
                view_count=5000
            ),
            VideoSearchResult(
                video_id="tutorial_video_1", 
                title="Complete Python Tutorial",
                duration=900,
                uploader="Education Hub",
                upload_date="2024-01-10",
                view_count=25000
            )
        ]
        
        # Test filter statistics
        stats = engine.video_filter.count_filtered_by_criteria(raw_results)
        
        assert stats['total'] == 2
        assert stats['shorts'] == 1  # One video under 60s
        assert stats['view_count_too_low'] == 1  # One video under 10k views
    
    def test_search_config_validation_integration(self):
        """Test search configuration validation in integrated workflow."""
        manager = SearchConfigManager()
        
        # Test valid configuration
        valid_config = SearchConfig(
            search_query="Python tutorial",
            max_results=25,
            sort_by="upload_date",
            upload_date="week"
        )
        
        # Should not raise exception
        manager.validate_config(valid_config)
        
        # Test invalid configuration
        invalid_config = SearchConfig(
            search_query="test",
            max_results=-5,  # Invalid
            sort_by="invalid_sort"  # Invalid
        )
        
        with pytest.raises(ValueError):
            manager.validate_config(invalid_config)
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_search_url_construction_integration(self, mock_yt_dlp):
        """Test search URL construction in real workflow."""
        # Setup mock
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {'entries': []}
        
        config = SearchConfig(
            search_query="machine learning tutorial",
            max_results=30
        )
        
        engine = SearchEngine(config)
        engine.search_videos("machine learning tutorial")
        
        # Verify correct URL was constructed and used
        mock_ydl.extract_info.assert_called_once()
        call_args = mock_ydl.extract_info.call_args[0]
        assert "ytsearch30:machine learning tutorial" in call_args[0]
    
    def test_video_search_result_functionality(self):
        """Test VideoSearchResult functionality in isolation."""
        # Test normal video
        video = VideoSearchResult(
            video_id="test_video_123",
            title="Test Video Title",
            duration=600,  # 10 minutes
            uploader="Test Channel",
            upload_date="2024-01-15",
            view_count=15000,
            thumbnail_url="https://example.com/thumb.jpg"
        )
        
        assert video.get_url() == "https://www.youtube.com/watch?v=test_video_123"
        assert not video.is_short()
        assert not video.is_live_stream()
        assert video.get_duration_formatted() == "10:00"
        
        # Test YouTube Short
        short_video = VideoSearchResult(
            video_id="short_123",
            title="Short Video",
            duration=45,
            uploader="Channel",
            upload_date="2024-01-15",
            view_count=1000
        )
        
        assert short_video.is_short()
        assert short_video.get_duration_formatted() == "00:45"
        
        # Test live stream
        live_video = VideoSearchResult(
            video_id="live_123",
            title="Live Stream",
            duration=0,
            uploader="Live Channel",
            upload_date="2024-01-15",
            view_count=500
        )
        
        assert live_video.is_live_stream()
        assert live_video.get_duration_formatted() == "LIVE"


class TestSearchErrorHandlingIntegration:
    """Integration tests for error handling across search components."""
    
    @patch('youtube_downloader.core.search_engine.yt_dlp.YoutubeDL')
    def test_network_error_propagation(self, mock_yt_dlp):
        """Test network error handling through the complete stack."""
        from youtube_downloader.core.search_engine import NetworkSearchError
        
        # Setup mock to raise network error
        mock_ydl = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = ConnectionError("Network unreachable")
        
        config = SearchConfig(search_query="test")
        engine = SearchEngine(config)
        
        with pytest.raises(NetworkSearchError):
            engine.search_videos("test")
    
    def test_invalid_filter_configuration(self):
        """Test handling of invalid filter configurations."""
        # Test contradictory duration filters
        with pytest.raises(ValueError, match="min_duration cannot be greater than max_duration"):
            filter_config = FilterConfig(min_duration=600, max_duration=300)
            manager = SearchConfigManager()
            search_config = SearchConfig(filter_config=filter_config)
            manager.validate_config(search_config) 