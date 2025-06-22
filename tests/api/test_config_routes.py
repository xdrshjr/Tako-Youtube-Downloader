"""
Tests for configuration-related API routes.
"""

import pytest
from unittest.mock import patch, Mock


class TestConfigRoutes:
    """Test cases for configuration-related API endpoints."""
    
    @patch('youtube_downloader.api.routes.config.config_manager')
    def test_get_config_success(self, mock_config_manager, api_client):
        """Test successful configuration retrieval."""
        # Mock the config manager
        mock_config = Mock()
        mock_config.quality = "best"
        mock_config.format = "mp4"
        mock_config.output_directory = "./downloads"
        mock_config.audio_format = "mp3"
        
        mock_config_manager.get_config.return_value = mock_config
        
        response = api_client.get("/api/v1/config/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "config" in data
        
        config = data["config"]
        assert config["quality"] == "best"
        assert config["format"] == "mp4"
        assert config["output_directory"] == "./downloads"
        assert config["audio_format"] == "mp3"
    
    @patch('youtube_downloader.api.routes.config.config_manager')
    def test_get_config_with_error(self, mock_config_manager, api_client):
        """Test configuration retrieval with error."""
        # Mock the config manager to raise an exception
        mock_config_manager.get_config.side_effect = Exception("Config error")
        
        response = api_client.get("/api/v1/config/")
        
        assert response.status_code == 500
    
    def test_get_default_config(self, api_client):
        """Test getting default configuration options."""
        response = api_client.get("/api/v1/config/defaults")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all expected options are present
        assert "quality_options" in data
        assert "format_options" in data
        assert "audio_format_options" in data
        assert "defaults" in data
        
        # Check specific values
        quality_options = data["quality_options"]
        assert "best" in quality_options
        assert "720p" in quality_options
        assert "1080p" in quality_options
        
        format_options = data["format_options"]
        assert "mp4" in format_options
        assert "webm" in format_options
        assert "mkv" in format_options
        
        audio_format_options = data["audio_format_options"]
        assert "mp3" in audio_format_options
        assert "aac" in audio_format_options
        assert "opus" in audio_format_options
        
        defaults = data["defaults"]
        assert defaults["quality"] == "best"
        assert defaults["format"] == "mp4"
        assert defaults["output_directory"] == "./downloads"
        assert defaults["audio_format"] == "mp3" 