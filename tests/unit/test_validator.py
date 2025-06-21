"""
Unit tests for URLValidator class.

Tests the URL validation, video ID extraction, and URL normalization functionality.
"""

import pytest
import json
import os
from pathlib import Path
from youtube_downloader.core.validator import URLValidator


class TestURLValidator:
    """Test cases for URLValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create URLValidator instance for testing."""
        return URLValidator()
    
    @pytest.fixture
    def sample_urls(self):
        """Load sample URLs from fixtures."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_urls.json"
        with open(fixture_path, 'r') as f:
            return json.load(f)
    
    def test_validate_youtube_url_valid_urls(self, validator, sample_urls):
        """Test validation of valid YouTube URLs."""
        for url in sample_urls["valid_urls"]:
            assert validator.validate_youtube_url(url), f"URL should be valid: {url}"
    
    def test_validate_youtube_url_invalid_urls(self, validator, sample_urls):
        """Test validation of invalid URLs."""
        for url in sample_urls["invalid_urls"]:
            assert not validator.validate_youtube_url(url), f"URL should be invalid: {url}"
    
    def test_extract_video_id_success(self, validator, sample_urls):
        """Test successful video ID extraction."""
        for url, expected_id in sample_urls["video_ids"].items():
            result = validator.extract_video_id(url)
            assert result == expected_id, f"Expected {expected_id}, got {result} for URL: {url}"
    
    def test_extract_video_id_invalid_url(self, validator):
        """Test video ID extraction with invalid URL."""
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            validator.extract_video_id("https://www.google.com")
    
    def test_normalize_url_standard_format(self, validator):
        """Test URL normalization to standard format."""
        test_cases = [
            ("https://youtu.be/dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ]
        
        for input_url, expected_url in test_cases:
            result = validator.normalize_url(input_url)
            assert result == expected_url, f"Expected {expected_url}, got {result}"
    
    def test_normalize_url_invalid_url(self, validator):
        """Test URL normalization with invalid URL."""
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            validator.normalize_url("https://www.google.com")
    
    def test_empty_url_handling(self, validator):
        """Test handling of empty URLs."""
        assert not validator.validate_youtube_url("")
        assert not validator.validate_youtube_url(None)
    
    def test_url_with_additional_parameters(self, validator):
        """Test URLs with additional parameters."""
        url_with_params = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=PLtest"
        assert validator.validate_youtube_url(url_with_params)
        assert validator.extract_video_id(url_with_params) == "dQw4w9WgXcQ"
    
    def test_youtube_shorts_support(self, validator):
        """Test YouTube Shorts URL support."""
        shorts_urls = [
            "https://www.youtube.com/shorts/FwYhFQHUn9g",
            "https://m.youtube.com/shorts/FwYhFQHUn9g",
            "https://youtube.com/shorts/FwYhFQHUn9g"
        ]
        
        for url in shorts_urls:
            assert validator.validate_youtube_url(url), f"Shorts URL should be valid: {url}"
            assert validator.extract_video_id(url) == "FwYhFQHUn9g", f"Should extract correct video ID from: {url}"
            
        # Test normalization
        normalized = validator.normalize_url("https://www.youtube.com/shorts/FwYhFQHUn9g")
        assert normalized == "https://www.youtube.com/watch?v=FwYhFQHUn9g" 