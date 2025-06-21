"""
Unit tests for ConfigManager class.

Tests configuration loading, validation, and management functionality.
"""

import pytest
import tempfile
import os
import yaml
from pathlib import Path
from youtube_downloader.core.config import ConfigManager, DownloadConfig


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        config_data = {
            'download': {
                'quality': '720p',
                'format': 'mp4',
                'audio_format': 'mp3'
            },
            'output': {
                'directory': './test_downloads',
                'naming_pattern': '{title}-{id}.{ext}',
                'create_subdirs': False
            },
            'network': {
                'concurrent_downloads': 2,
                'retry_attempts': 3,
                'timeout': 30,
                'rate_limit': None
            },
            'logging': {
                'level': 'INFO',
                'file': 'test.log',
                'max_size': '10MB',
                'backup_count': 5
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_file = f.name
        
        yield temp_file
        os.unlink(temp_file)
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        assert isinstance(config, DownloadConfig)
        assert config.quality == "best"
        assert config.format == "mp4"
        assert config.output_directory == "./downloads"
    
    def test_load_custom_config_file(self, temp_config_file):
        """Test loading custom configuration file."""
        config_manager = ConfigManager(config_file=temp_config_file)
        config = config_manager.get_config()
        
        assert config.quality == "720p"
        assert config.format == "mp4"
        assert config.output_directory == "./test_downloads"
        assert config.retry_attempts == 3
    
    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        config_manager = ConfigManager()
        valid_config = DownloadConfig(
            quality="720p",
            format="mp4",
            audio_format="mp3",
            output_directory="./downloads",
            naming_pattern="{title}-{id}.{ext}",
            create_subdirs=False,
            concurrent_downloads=3,
            retry_attempts=3,
            timeout=30,
            rate_limit=None
        )
        
        # Should not raise any exception
        config_manager.validate_config(valid_config)
    
    def test_validate_config_invalid_quality(self):
        """Test validation with invalid quality setting."""
        config_manager = ConfigManager()
        invalid_config = DownloadConfig(
            quality="invalid_quality",
            format="mp4",
            audio_format="mp3",
            output_directory="./downloads"
        )
        
        with pytest.raises(ValueError, match="Invalid quality"):
            config_manager.validate_config(invalid_config)
    
    def test_validate_config_invalid_format(self):
        """Test validation with invalid format setting."""
        config_manager = ConfigManager()
        invalid_config = DownloadConfig(
            quality="720p",
            format="invalid_format",
            audio_format="mp3",
            output_directory="./downloads"
        )
        
        with pytest.raises(ValueError, match="Invalid format"):
            config_manager.validate_config(invalid_config)
    
    def test_update_config(self):
        """Test updating configuration values."""
        config_manager = ConfigManager()
        original_config = config_manager.get_config()
        
        config_manager.update_config(quality="1080p", format="webm")
        updated_config = config_manager.get_config()
        
        assert updated_config.quality == "1080p"
        assert updated_config.format == "webm"
        assert updated_config.output_directory == original_config.output_directory  # Should remain unchanged
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to file."""
        config_file = tmp_path / "test_config.yaml"
        config_manager = ConfigManager()
        config_manager.update_config(quality="1080p", format="webm")
        
        config_manager.save_config(str(config_file))
        
        # Verify file was created and contains correct data
        assert config_file.exists()
        with open(config_file, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data['download']['quality'] == '1080p'
        assert saved_data['download']['format'] == 'webm'
    
    def test_config_file_not_found(self):
        """Test handling of non-existent config file."""
        with pytest.raises(FileNotFoundError):
            ConfigManager(config_file="non_existent_file.yaml")
    
    def test_invalid_yaml_config(self, tmp_path):
        """Test handling of invalid YAML config file."""
        invalid_config_file = tmp_path / "invalid.yaml"
        invalid_config_file.write_text("invalid: yaml: content: [")
        
        with pytest.raises(yaml.YAMLError):
            ConfigManager(config_file=str(invalid_config_file)) 