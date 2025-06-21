"""
Unit tests for video filter module.

This module tests the VideoFilter class that provides filtering functionality
for YouTube search results based on various criteria.
"""

import pytest
from datetime import datetime, timedelta

from youtube_downloader.core.video_filter import (
    VideoFilter,
    VideoSearchResult
)
from youtube_downloader.core.search_config import FilterConfig


class TestVideoSearchResult:
    """Test cases for VideoSearchResult data class."""
    
    def test_video_search_result_initialization(self):
        """Test VideoSearchResult initialization with all fields."""
        result = VideoSearchResult(
            video_id="test_id_123",
            title="Test Video Title",
            duration=300,
            uploader="Test Channel",
            upload_date="2024-01-15",
            view_count=10000,
            thumbnail_url="https://example.com/thumb.jpg",
            description="Test description",
            like_count=500
        )
        
        assert result.video_id == "test_id_123"
        assert result.title == "Test Video Title"
        assert result.duration == 300
        assert result.uploader == "Test Channel"
        assert result.upload_date == "2024-01-15"
        assert result.view_count == 10000
        assert result.thumbnail_url == "https://example.com/thumb.jpg"
        assert result.description == "Test description"
        assert result.like_count == 500
    
    def test_video_search_result_minimal_initialization(self):
        """Test VideoSearchResult with minimal required fields."""
        result = VideoSearchResult(
            video_id="test_id",
            title="Test Title",
            duration=180,
            uploader="Channel",
            upload_date="2024-01-01",
            view_count=1000
        )
        
        assert result.video_id == "test_id"
        assert result.title == "Test Title"
        assert result.duration == 180
        assert result.thumbnail_url is None
        assert result.description is None
        assert result.like_count is None
    
    def test_video_search_result_url_generation(self):
        """Test generating YouTube URL from video ID."""
        result = VideoSearchResult(
            video_id="dQw4w9WgXcQ",
            title="Test",
            duration=60,
            uploader="Channel",
            upload_date="2024-01-01",
            view_count=1000
        )
        
        expected_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert result.get_url() == expected_url


class TestVideoFilter:
    """Test cases for VideoFilter class."""
    
    def create_sample_videos(self):
        """Create sample video results for testing."""
        return [
            VideoSearchResult(
                video_id="short_video",
                title="Short Video",
                duration=30,  # 30 seconds - YouTube Short
                uploader="Channel A",
                upload_date="2024-01-15",
                view_count=5000
            ),
            VideoSearchResult(
                video_id="medium_video",
                title="Medium Length Video",
                duration=300,  # 5 minutes
                uploader="Channel B", 
                upload_date="2024-01-10",
                view_count=15000
            ),
            VideoSearchResult(
                video_id="long_video",
                title="Long Tutorial Video",
                duration=1800,  # 30 minutes
                uploader="Channel C",
                upload_date="2024-01-05",
                view_count=50000
            ),
            VideoSearchResult(
                video_id="live_stream",
                title="Live Stream - Current",
                duration=0,  # Live streams have 0 duration
                uploader="Channel D",
                upload_date="2024-01-15",
                view_count=2000
            )
        ]
    
    def test_video_filter_initialization_default(self):
        """Test VideoFilter initialization with default config."""
        filter_config = FilterConfig()
        video_filter = VideoFilter(filter_config)
        
        assert video_filter.filter_config == filter_config
    
    def test_video_filter_initialization_custom(self):
        """Test VideoFilter initialization with custom config."""
        filter_config = FilterConfig(
            min_duration=60,
            max_duration=600,
            exclude_shorts=True,
            exclude_live=True
        )
        video_filter = VideoFilter(filter_config)
        
        assert video_filter.filter_config.min_duration == 60
        assert video_filter.filter_config.max_duration == 600
        assert video_filter.filter_config.exclude_shorts is True
        assert video_filter.filter_config.exclude_live is True
    
    def test_filter_by_duration_min_only(self):
        """Test filtering by minimum duration only."""
        filter_config = FilterConfig(min_duration=120)  # 2 minutes
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.filter_by_duration(videos)
        
        # Should keep medium (300s) and long (1800s) videos
        assert len(filtered) == 2
        assert filtered[0].video_id == "medium_video"
        assert filtered[1].video_id == "long_video"
    
    def test_filter_by_duration_max_only(self):
        """Test filtering by maximum duration only."""
        filter_config = FilterConfig(max_duration=600)  # 10 minutes
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.filter_by_duration(videos)
        
        # Should keep short (30s), medium (300s), and live (0s) videos
        assert len(filtered) == 3
        video_ids = [v.video_id for v in filtered]
        assert "short_video" in video_ids
        assert "medium_video" in video_ids
        assert "live_stream" in video_ids
    
    def test_filter_by_duration_range(self):
        """Test filtering by duration range."""
        filter_config = FilterConfig(min_duration=60, max_duration=900)  # 1-15 minutes
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.filter_by_duration(videos)
        
        # Should keep only medium video (300s)
        assert len(filtered) == 1
        assert filtered[0].video_id == "medium_video"
    
    def test_filter_by_view_count(self):
        """Test filtering by minimum view count."""
        filter_config = FilterConfig(min_view_count=10000)
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.filter_by_view_count(videos)
        
        # Should keep medium (15k) and long (50k) videos
        assert len(filtered) == 2
        video_ids = [v.video_id for v in filtered]
        assert "medium_video" in video_ids
        assert "long_video" in video_ids
    
    def test_exclude_shorts(self):
        """Test excluding YouTube Shorts (videos under 60 seconds)."""
        filter_config = FilterConfig(exclude_shorts=True)
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.exclude_shorts_filter(videos)
        
        # Should exclude short video (30s)
        assert len(filtered) == 3
        video_ids = [v.video_id for v in filtered]
        assert "short_video" not in video_ids
        assert "medium_video" in video_ids
        assert "long_video" in video_ids
        assert "live_stream" in video_ids
    
    def test_exclude_live_streams(self):
        """Test excluding live streams (videos with 0 duration)."""
        filter_config = FilterConfig(exclude_live=True)
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.exclude_live_filter(videos)
        
        # Should exclude live stream (0 duration)
        assert len(filtered) == 3
        video_ids = [v.video_id for v in filtered]
        assert "live_stream" not in video_ids
        assert "short_video" in video_ids
        assert "medium_video" in video_ids
        assert "long_video" in video_ids
    
    def test_filter_by_upload_date(self):
        """Test filtering by upload date."""
        # Test filtering to keep only videos from last week
        cutoff_date = "2024-01-10"
        filter_config = FilterConfig(min_upload_date=cutoff_date)
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.filter_by_upload_date(videos)
        
        # Should keep videos uploaded on or after 2024-01-10
        assert len(filtered) == 3
        video_ids = [v.video_id for v in filtered]
        assert "short_video" in video_ids  # 2024-01-15
        assert "medium_video" in video_ids  # 2024-01-10
        assert "live_stream" in video_ids  # 2024-01-15
        assert "long_video" not in video_ids  # 2024-01-05
    
    def test_apply_all_filters_combined(self):
        """Test applying all filters together."""
        filter_config = FilterConfig(
            min_duration=120,  # At least 2 minutes
            max_duration=900,  # At most 15 minutes
            min_view_count=10000,  # At least 10k views
            exclude_shorts=True,
            exclude_live=True,
            min_upload_date="2024-01-08"
        )
        
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.apply_all_filters(videos)
        
        # Should keep only medium video:
        # - Duration 300s (within 120-900s range)
        # - View count 15k (>= 10k)
        # - Not a short (>60s)
        # - Not live (duration > 0)
        # - Upload date 2024-01-10 (>= 2024-01-08)
        assert len(filtered) == 1
        assert filtered[0].video_id == "medium_video"
    
    def test_apply_all_filters_no_restrictions(self):
        """Test applying filters with no restrictions."""
        filter_config = FilterConfig()  # Default config with minimal filtering
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.apply_all_filters(videos)
        
        # Should exclude shorts and live streams by default
        assert len(filtered) == 2
        video_ids = [v.video_id for v in filtered]
        assert "medium_video" in video_ids
        assert "long_video" in video_ids
    
    def test_empty_video_list(self):
        """Test filtering empty video list."""
        filter_config = FilterConfig(min_duration=60)
        video_filter = VideoFilter(filter_config)
        
        filtered = video_filter.apply_all_filters([])
        
        assert filtered == []
    
    def test_no_videos_match_criteria(self):
        """Test when no videos match the filtering criteria."""
        filter_config = FilterConfig(
            min_duration=3600,  # 1 hour minimum
            min_view_count=100000  # 100k minimum views
        )
        
        video_filter = VideoFilter(filter_config)
        videos = self.create_sample_videos()
        
        filtered = video_filter.apply_all_filters(videos)
        
        assert len(filtered) == 0


class TestVideoFilterEdgeCases:
    """Test edge cases and error conditions for VideoFilter."""
    
    def test_invalid_upload_date_format(self):
        """Test handling of invalid upload date format."""
        filter_config = FilterConfig(min_upload_date="invalid-date")
        video_filter = VideoFilter(filter_config)
        
        videos = [
            VideoSearchResult(
                video_id="test",
                title="Test",
                duration=60,
                uploader="Channel",
                upload_date="2024-01-15",
                view_count=1000
            )
        ]
        
        # Should handle gracefully and log warning
        filtered = video_filter.filter_by_upload_date(videos)
        # Without valid date parsing, should return original list
        assert len(filtered) == 1
    
    def test_missing_optional_fields(self):
        """Test filtering videos with missing optional fields."""
        videos = [
            VideoSearchResult(
                video_id="test",
                title="Test Video",
                duration=300,
                uploader="Channel",
                upload_date="2024-01-15",
                view_count=5000,
                # Missing optional fields: thumbnail_url, description, like_count
            )
        ]
        
        filter_config = FilterConfig(min_view_count=1000)
        video_filter = VideoFilter(filter_config)
        
        filtered = video_filter.apply_all_filters(videos)
        
        assert len(filtered) == 1
        assert filtered[0].video_id == "test" 