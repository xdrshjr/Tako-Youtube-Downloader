"""
Configuration management module for YouTube Downloader.

This module provides configuration management functionality including loading,
validation, and updating of download settings.
"""

import yaml
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class DownloadConfig:
    """
    Configuration data class for download settings.
    
    Contains all configurable parameters for video downloading.
    """
    # Download settings
    quality: str = "best"
    format: str = "mp4"
    audio_format: str = "mp3"
    
    # Output settings
    output_directory: str = "./downloads"
    naming_pattern: str = "{title}-{id}.{ext}"
    create_subdirs: bool = False
    
    # Network settings
    concurrent_downloads: int = 3
    retry_attempts: int = 3
    timeout: int = 30
    rate_limit: Optional[int] = None
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "downloader.log"
    max_log_size: str = "10MB"
    backup_count: int = 5


class ConfigManager:
    """
    Manages application configuration.
    
    Handles loading configuration from files, validation, and runtime updates.
    """
    
    # Valid options for configuration validation
    VALID_QUALITIES = ["best", "worst", "720p", "1080p", "480p", "360p", "240p", "144p"]
    VALID_FORMATS = ["mp4", "webm", "mkv", "flv", "3gp"]
    VALID_AUDIO_FORMATS = ["mp3", "aac", "opus", "m4a", "wav"]
    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to custom configuration file. If None, uses default config.
        """
        self._config: DownloadConfig = DownloadConfig()
        
        if config_file:
            if not Path(config_file).exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            self._load_config_from_file(config_file)
        else:
            self._load_default_config()
    
    def get_config(self) -> DownloadConfig:
        """
        Get current configuration.
        
        Returns:
            DownloadConfig: Current configuration object
        """
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration values.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        # Validate updated configuration
        self.validate_config(self._config)
    
    def validate_config(self, config: DownloadConfig) -> None:
        """
        Validate configuration values.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValueError: If configuration contains invalid values
        """
        # Validate quality
        if config.quality not in self.VALID_QUALITIES:
            raise ValueError(f"Invalid quality: {config.quality}. Valid options: {self.VALID_QUALITIES}")
        
        # Validate format
        if config.format not in self.VALID_FORMATS:
            raise ValueError(f"Invalid format: {config.format}. Valid options: {self.VALID_FORMATS}")
        
        # Validate audio format
        if config.audio_format not in self.VALID_AUDIO_FORMATS:
            raise ValueError(f"Invalid audio format: {config.audio_format}. Valid options: {self.VALID_AUDIO_FORMATS}")
        
        # Validate log level
        if config.log_level not in self.VALID_LOG_LEVELS:
            raise ValueError(f"Invalid log level: {config.log_level}. Valid options: {self.VALID_LOG_LEVELS}")
        
        # Validate numeric values
        if config.concurrent_downloads <= 0:
            raise ValueError("Concurrent downloads must be greater than 0")
        
        if config.retry_attempts < 0:
            raise ValueError("Retry attempts must be non-negative")
        
        if config.timeout <= 0:
            raise ValueError("Timeout must be greater than 0")
        
        if config.backup_count < 0:
            raise ValueError("Backup count must be non-negative")
    
    def save_config(self, file_path: str) -> None:
        """
        Save current configuration to file.
        
        Args:
            file_path: Path to save configuration file
        """
        config_dict = self._config_to_dict(self._config)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def _load_default_config(self) -> None:
        """Load default configuration."""
        # Try to load from default config file
        default_config_path = Path(__file__).parent.parent.parent.parent / "config" / "default_config.yaml"
        
        if default_config_path.exists():
            self._load_config_from_file(str(default_config_path))
        else:
            # Use hardcoded defaults if config file doesn't exist
            self._config = DownloadConfig()
    
    def _load_config_from_file(self, file_path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to configuration file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return
            
            # Extract configuration values
            download_config = config_data.get('download', {})
            output_config = config_data.get('output', {})
            network_config = config_data.get('network', {})
            logging_config = config_data.get('logging', {})
            
            # Create configuration object
            self._config = DownloadConfig(
                # Download settings
                quality=download_config.get('quality', self._config.quality),
                format=download_config.get('format', self._config.format),
                audio_format=download_config.get('audio_format', self._config.audio_format),
                
                # Output settings
                output_directory=output_config.get('directory', self._config.output_directory),
                naming_pattern=output_config.get('naming_pattern', self._config.naming_pattern),
                create_subdirs=output_config.get('create_subdirs', self._config.create_subdirs),
                
                # Network settings
                concurrent_downloads=network_config.get('concurrent_downloads', self._config.concurrent_downloads),
                retry_attempts=network_config.get('retry_attempts', self._config.retry_attempts),
                timeout=network_config.get('timeout', self._config.timeout),
                rate_limit=network_config.get('rate_limit', self._config.rate_limit),
                
                # Logging settings
                log_level=logging_config.get('level', self._config.log_level),
                log_file=logging_config.get('file', self._config.log_file),
                max_log_size=logging_config.get('max_size', self._config.max_log_size),
                backup_count=logging_config.get('backup_count', self._config.backup_count)
            )
            
            # Validate loaded configuration
            self.validate_config(self._config)
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML configuration file: {e}")
        except Exception as e:
            raise Exception(f"Error loading configuration file: {e}")
    
    def _config_to_dict(self, config: DownloadConfig) -> Dict[str, Any]:
        """
        Convert configuration object to dictionary for serialization.
        
        Args:
            config: Configuration object to convert
            
        Returns:
            Dict[str, Any]: Configuration as nested dictionary
        """
        return {
            'download': {
                'quality': config.quality,
                'format': config.format,
                'audio_format': config.audio_format
            },
            'output': {
                'directory': config.output_directory,
                'naming_pattern': config.naming_pattern,
                'create_subdirs': config.create_subdirs
            },
            'network': {
                'concurrent_downloads': config.concurrent_downloads,
                'retry_attempts': config.retry_attempts,
                'timeout': config.timeout,
                'rate_limit': config.rate_limit
            },
            'logging': {
                'level': config.log_level,
                'file': config.log_file,
                'max_size': config.max_log_size,
                'backup_count': config.backup_count
            }
        } 