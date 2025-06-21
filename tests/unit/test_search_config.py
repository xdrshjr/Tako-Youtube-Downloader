"""
Unit tests for search configuration module.

This module tests the SearchConfig and FilterConfig classes that manage
search parameters, filtering options, and batch download settings.
"""

import pytest
from dataclasses import asdict
from pathlib import Path

from youtube_downloader.core.search_config import (
    FilterConfig,
    SearchConfig,
    SearchConfigManager
)
from youtube_downloader.core.config import DownloadConfig


class TestFilterConfig:
    """Test cases for FilterConfig class."""
    
    def test_filter_config_default_initialization(self):
        """Test FilterConfig with default values."""
        config = FilterConfig()
        
        assert config.min_duration is None
        assert config.max_duration is None
        assert config.min_quality is None
        assert config.exclude_shorts is True
        assert config.exclude_live is True
    
    def test_filter_config_custom_initialization(self):
        """Test FilterConfig with custom values."""
        config = FilterConfig(
            min_duration=60,
            max_duration=600,
            min_quality="720p",
            exclude_shorts=False,
            exclude_live=False
        )
        
        assert config.min_duration == 60
        assert config.max_duration == 600
        assert config.min_quality == "720p"
        assert config.exclude_shorts is False
        assert config.exclude_live is False
    
    def test_filter_config_validation_duration_range(self):
        """Test duration range validation."""
        # Valid range
        config = FilterConfig(min_duration=60, max_duration=300)
        assert config.min_duration < config.max_duration
        
        # Edge case: equal values should be valid
        config = FilterConfig(min_duration=120, max_duration=120)
        assert config.min_duration == config.max_duration


class TestSearchConfig:
    """Test cases for SearchConfig class."""
    
    def test_search_config_default_initialization(self):
        """Test SearchConfig with default values."""
        config = SearchConfig()
        
        assert config.search_query == ""
        assert config.max_results == 10
        assert config.sort_by == "relevance"
        assert config.upload_date == "any"
        assert isinstance(config.filter_config, FilterConfig)
        assert isinstance(config.download_config, DownloadConfig)
        assert config.max_concurrent_downloads == 3
        assert config.retry_failed_downloads is True
    
    def test_search_config_custom_initialization(self):
        """Test SearchConfig with custom values."""
        filter_config = FilterConfig(min_duration=120, max_duration=480)
        download_config = DownloadConfig(quality="720p", format="mp4")
        
        config = SearchConfig(
            search_query="Python tutorial",
            max_results=25,
            sort_by="upload_date",
            upload_date="week",
            filter_config=filter_config,
            download_config=download_config,
            max_concurrent_downloads=5,
            retry_failed_downloads=False
        )
        
        assert config.search_query == "Python tutorial"
        assert config.max_results == 25
        assert config.sort_by == "upload_date"
        assert config.upload_date == "week"
        assert config.filter_config == filter_config
        assert config.download_config == download_config
        assert config.max_concurrent_downloads == 5
        assert config.retry_failed_downloads is False
    
    def test_search_config_with_string_query(self):
        """Test SearchConfig initialization with string query."""
        config = SearchConfig.from_query("machine learning", max_results=15)
        
        assert config.search_query == "machine learning"
        assert config.max_results == 15
        assert config.sort_by == "relevance"


class TestSearchConfigManager:
    """Test cases for SearchConfigManager class."""
    
    def test_search_config_manager_initialization(self):
        """Test SearchConfigManager initialization."""
        manager = SearchConfigManager()
        
        assert isinstance(manager.get_config(), SearchConfig)
    
    def test_search_config_manager_with_custom_config(self):
        """Test SearchConfigManager with custom configuration."""
        custom_config = SearchConfig(
            search_query="test query",
            max_results=20
        )
        
        manager = SearchConfigManager(custom_config)
        config = manager.get_config()
        
        assert config.search_query == "test query"
        assert config.max_results == 20
    
    def test_update_search_config(self):
        """Test updating search configuration."""
        manager = SearchConfigManager()
        
        manager.update_config(
            search_query="updated query",
            max_results=50,
            sort_by="view_count"
        )
        
        config = manager.get_config()
        assert config.search_query == "updated query"
        assert config.max_results == 50
        assert config.sort_by == "view_count"
    
    def test_validate_config_valid_values(self):
        """Test configuration validation with valid values."""
        manager = SearchConfigManager()
        
        valid_config = SearchConfig(
            search_query="test",
            max_results=25,
            sort_by="upload_date",
            upload_date="month"
        )
        
        # Should not raise any exception
        manager.validate_config(valid_config)
    
    def test_validate_config_invalid_sort_by(self):
        """Test configuration validation with invalid sort_by."""
        manager = SearchConfigManager()
        
        invalid_config = SearchConfig(
            search_query="test",
            sort_by="invalid_sort"
        )
        
        with pytest.raises(ValueError, match="Invalid sort_by"):
            manager.validate_config(invalid_config)
    
    def test_validate_config_invalid_upload_date(self):
        """Test configuration validation with invalid upload_date."""
        manager = SearchConfigManager()
        
        invalid_config = SearchConfig(
            search_query="test",
            upload_date="invalid_date"
        )
        
        with pytest.raises(ValueError, match="Invalid upload_date"):
            manager.validate_config(invalid_config)
    
    def test_validate_config_invalid_max_results(self):
        """Test configuration validation with invalid max_results."""
        manager = SearchConfigManager()
        
        # Test negative value
        invalid_config = SearchConfig(
            search_query="test",
            max_results=-5
        )
        
        with pytest.raises(ValueError, match="max_results must be positive"):
            manager.validate_config(invalid_config)
        
        # Test zero value
        invalid_config.max_results = 0
        with pytest.raises(ValueError, match="max_results must be positive"):
            manager.validate_config(invalid_config)
    
    def test_validate_config_invalid_max_concurrent_downloads(self):
        """Test configuration validation with invalid max_concurrent_downloads."""
        manager = SearchConfigManager()
        
        invalid_config = SearchConfig(
            search_query="test",
            max_concurrent_downloads=0
        )
        
        with pytest.raises(ValueError, match="max_concurrent_downloads must be positive"):
            manager.validate_config(invalid_config)
    
    def test_config_to_dict(self):
        """Test converting configuration to dictionary."""
        manager = SearchConfigManager()
        filter_config = FilterConfig(min_duration=60, max_duration=300)
        
        config = SearchConfig(
            search_query="test query",
            max_results=15,
            filter_config=filter_config
        )
        
        config_dict = manager._config_to_dict(config)
        
        assert config_dict["search"]["query"] == "test query"
        assert config_dict["search"]["max_results"] == 15
        assert config_dict["filter"]["min_duration"] == 60
        assert config_dict["filter"]["max_duration"] == 300
    
    def test_config_from_dict(self):
        """Test creating configuration from dictionary."""
        manager = SearchConfigManager()
        
        config_dict = {
            "search": {
                "query": "test query",
                "max_results": 20,
                "sort_by": "view_count"
            },
            "filter": {
                "min_duration": 120,
                "exclude_shorts": False
            },
            "batch": {
                "max_concurrent_downloads": 5
            }
        }
        
        config = manager._config_from_dict(config_dict)
        
        assert config.search_query == "test query"
        assert config.max_results == 20
        assert config.sort_by == "view_count"
        assert config.filter_config.min_duration == 120
        assert config.filter_config.exclude_shorts is False
        assert config.max_concurrent_downloads == 5


class TestSearchConfigIntegration:
    """Integration tests for search configuration."""
    
    def test_search_config_with_download_config_integration(self):
        """Test SearchConfig integration with DownloadConfig."""
        download_config = DownloadConfig(
            quality="1080p",
            format="mp4",
            output_directory="./test_downloads"
        )
        
        search_config = SearchConfig(
            search_query="integration test",
            download_config=download_config
        )
        
        assert search_config.download_config.quality == "1080p"
        assert search_config.download_config.format == "mp4"
        assert search_config.download_config.output_directory == "./test_downloads"
    
    def test_filter_config_duration_consistency(self):
        """Test FilterConfig duration range consistency."""
        # Test that min_duration <= max_duration when both are set
        filter_config = FilterConfig(min_duration=300, max_duration=100)
        
        # This should be handled by validation in SearchConfigManager
        manager = SearchConfigManager()
        search_config = SearchConfig(filter_config=filter_config)
        
        with pytest.raises(ValueError, match="min_duration cannot be greater than max_duration"):
            manager.validate_config(search_config) 