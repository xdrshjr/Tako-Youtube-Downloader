"""
Search configuration management module for YouTube Downloader.

This module provides configuration management for search functionality including
search parameters, filtering options, and batch download settings.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
import logging

from .config import DownloadConfig


@dataclass
class FilterConfig:
    """
    Configuration for video filtering parameters.
    
    Contains all filterable parameters for search results including duration,
    quality, and content type filtering.
    """
    # Duration filtering (in seconds)
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    
    # Quality filtering
    min_quality: Optional[str] = None  # "720p", "1080p", etc.
    
    # Content type filtering
    exclude_shorts: bool = True
    exclude_live: bool = True
    
    # Upload date filtering
    min_upload_date: Optional[str] = None  # ISO format or relative like "2023-01-01"
    
    # View count filtering
    min_view_count: Optional[int] = None


@dataclass  
class SearchConfig:
    """
    Configuration for YouTube search and batch download parameters.
    
    Contains search query, result limits, sorting options, filtering settings,
    and batch download configuration.
    """
    # Search parameters
    search_query: str = ""
    max_results: int = 10
    sort_by: str = "relevance"  # "relevance", "upload_date", "view_count", "rating"
    upload_date: str = "any"    # "hour", "today", "week", "month", "year", "any"
    
    # Filtering configuration
    filter_config: FilterConfig = field(default_factory=FilterConfig)
    
    # Download configuration (inherited from existing system)
    download_config: DownloadConfig = field(default_factory=DownloadConfig)
    
    # Batch download parameters
    max_concurrent_downloads: int = 3
    retry_failed_downloads: bool = True
    
    @classmethod
    def from_query(cls, query: str, max_results: int = 10, **kwargs) -> 'SearchConfig':
        """
        Create SearchConfig from a query string with optional parameters.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            **kwargs: Additional configuration parameters
            
        Returns:
            SearchConfig: Configured search configuration object
        """
        return cls(
            search_query=query,
            max_results=max_results,
            **kwargs
        )


class SearchConfigManager:
    """
    Manages search configuration with validation and persistence.
    
    Provides configuration validation, format conversion, and integration
    with the existing configuration system.
    """
    
    # Valid options for configuration validation
    VALID_SORT_BY = ["relevance", "upload_date", "view_count", "rating"]
    VALID_UPLOAD_DATE = ["hour", "today", "week", "month", "year", "any"]
    VALID_QUALITIES = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """
        Initialize the search configuration manager.
        
        Args:
            config: Optional initial SearchConfig. If None, uses default config.
        """
        self._config: SearchConfig = config if config is not None else SearchConfig()
        self._logger = logging.getLogger(__name__)
        
        # Validate initial configuration
        self.validate_config(self._config)
        
        self._logger.info("SearchConfigManager initialized", extra={
            'search_query': self._config.search_query,
            'max_results': self._config.max_results,
            'sort_by': self._config.sort_by
        })
    
    def get_config(self) -> SearchConfig:
        """
        Get current search configuration.
        
        Returns:
            SearchConfig: Current search configuration object
        """
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        Update search configuration values.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Raises:
            ValueError: If any updated configuration values are invalid
        """
        # Create a copy of current config for validation
        updated_values = {}
        
        # Handle nested config updates
        for key, value in kwargs.items():
            if key.startswith('filter_'):
                # Filter config updates
                filter_key = key[7:]  # Remove 'filter_' prefix
                if not hasattr(self._config.filter_config, filter_key):
                    raise ValueError(f"Invalid filter configuration key: {filter_key}")
                setattr(self._config.filter_config, filter_key, value)
            elif key.startswith('download_'):
                # Download config updates
                download_key = key[9:]  # Remove 'download_' prefix
                if not hasattr(self._config.download_config, download_key):
                    raise ValueError(f"Invalid download configuration key: {download_key}")
                setattr(self._config.download_config, download_key, value)
            else:
                # Direct config updates
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
                    updated_values[key] = value
                else:
                    raise ValueError(f"Invalid configuration key: {key}")
        
        # Validate updated configuration
        self.validate_config(self._config)
        
        self._logger.info("Search configuration updated", extra=updated_values)
    
    def validate_config(self, config: SearchConfig) -> None:
        """
        Validate search configuration values.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValueError: If configuration contains invalid values
        """
        # Validate sort_by
        if config.sort_by not in self.VALID_SORT_BY:
            raise ValueError(f"Invalid sort_by: {config.sort_by}. "
                           f"Valid options: {self.VALID_SORT_BY}")
        
        # Validate upload_date
        if config.upload_date not in self.VALID_UPLOAD_DATE:
            raise ValueError(f"Invalid upload_date: {config.upload_date}. "
                           f"Valid options: {self.VALID_UPLOAD_DATE}")
        
        # Validate max_results
        if config.max_results <= 0:
            raise ValueError("max_results must be positive")
        
        # Validate max_concurrent_downloads
        if config.max_concurrent_downloads <= 0:
            raise ValueError("max_concurrent_downloads must be positive")
        
        # Validate filter configuration
        self._validate_filter_config(config.filter_config)
        
        # Use existing ConfigManager to validate download config
        from .config import ConfigManager
        config_manager = ConfigManager()
        config_manager.validate_config(config.download_config)
    
    def _validate_filter_config(self, filter_config: FilterConfig) -> None:
        """
        Validate filter configuration values.
        
        Args:
            filter_config: Filter configuration to validate
            
        Raises:
            ValueError: If filter configuration contains invalid values
        """
        # Validate duration range
        if (filter_config.min_duration is not None and 
            filter_config.max_duration is not None and
            filter_config.min_duration > filter_config.max_duration):
            raise ValueError("min_duration cannot be greater than max_duration")
        
        # Validate duration values are non-negative
        if filter_config.min_duration is not None and filter_config.min_duration < 0:
            raise ValueError("min_duration must be non-negative")
        
        if filter_config.max_duration is not None and filter_config.max_duration < 0:
            raise ValueError("max_duration must be non-negative")
        
        # Validate quality
        if (filter_config.min_quality is not None and 
            filter_config.min_quality not in self.VALID_QUALITIES):
            raise ValueError(f"Invalid min_quality: {filter_config.min_quality}. "
                           f"Valid options: {self.VALID_QUALITIES}")
        
        # Validate view count
        if filter_config.min_view_count is not None and filter_config.min_view_count < 0:
            raise ValueError("min_view_count must be non-negative")
    
    def save_config(self, file_path: str) -> None:
        """
        Save current search configuration to file.
        
        Args:
            file_path: Path to save configuration file
        """
        import yaml
        config_dict = self._config_to_dict(self._config)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        self._logger.info(f"Search configuration saved to {file_path}")
    
    def load_config(self, file_path: str) -> None:
        """
        Load search configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration file contains invalid values
        """
        import yaml
        from pathlib import Path
        
        config_file = Path(file_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        if config_data:
            self._config = self._config_from_dict(config_data)
            self.validate_config(self._config)
        
        self._logger.info(f"Search configuration loaded from {file_path}")
    
    def _config_to_dict(self, config: SearchConfig) -> Dict[str, Any]:
        """
        Convert SearchConfig to dictionary format.
        
        Args:
            config: Configuration to convert
            
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            "search": {
                "query": config.search_query,
                "max_results": config.max_results,
                "sort_by": config.sort_by,
                "upload_date": config.upload_date
            },
            "filter": {
                "min_duration": config.filter_config.min_duration,
                "max_duration": config.filter_config.max_duration,
                "min_quality": config.filter_config.min_quality,
                "exclude_shorts": config.filter_config.exclude_shorts,
                "exclude_live": config.filter_config.exclude_live,
                "min_upload_date": config.filter_config.min_upload_date,
                "min_view_count": config.filter_config.min_view_count
            },
            "download": {
                "quality": config.download_config.quality,
                "format": config.download_config.format,
                "audio_format": config.download_config.audio_format,
                "output_directory": config.download_config.output_directory,
                "naming_pattern": config.download_config.naming_pattern,
                "create_subdirs": config.download_config.create_subdirs
            },
            "batch": {
                "max_concurrent_downloads": config.max_concurrent_downloads,
                "retry_failed_downloads": config.retry_failed_downloads
            }
        }
    
    def _config_from_dict(self, config_dict: Dict[str, Any]) -> SearchConfig:
        """
        Create SearchConfig from dictionary format.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            SearchConfig: Configuration object
        """
        # Extract sections with defaults
        search_config = config_dict.get('search', {})
        filter_config = config_dict.get('filter', {})
        download_config = config_dict.get('download', {})
        batch_config = config_dict.get('batch', {})
        
        # Create filter configuration
        filter_obj = FilterConfig(
            min_duration=filter_config.get('min_duration'),
            max_duration=filter_config.get('max_duration'),
            min_quality=filter_config.get('min_quality'),
            exclude_shorts=filter_config.get('exclude_shorts', True),
            exclude_live=filter_config.get('exclude_live', True),
            min_upload_date=filter_config.get('min_upload_date'),
            min_view_count=filter_config.get('min_view_count')
        )
        
        # Create download configuration
        download_obj = DownloadConfig(
            quality=download_config.get('quality', 'best'),
            format=download_config.get('format', 'mp4'),
            audio_format=download_config.get('audio_format', 'mp3'),
            output_directory=download_config.get('output_directory', './downloads'),
            naming_pattern=download_config.get('naming_pattern', '{title}-{id}.{ext}'),
            create_subdirs=download_config.get('create_subdirs', False)
        )
        
        # Create search configuration
        return SearchConfig(
            search_query=search_config.get('query', ''),
            max_results=search_config.get('max_results', 10),
            sort_by=search_config.get('sort_by', 'relevance'),
            upload_date=search_config.get('upload_date', 'any'),
            filter_config=filter_obj,
            download_config=download_obj,
            max_concurrent_downloads=batch_config.get('max_concurrent_downloads', 3),
            retry_failed_downloads=batch_config.get('retry_failed_downloads', True)
        )
    
    def get_yt_dlp_search_options(self) -> Dict[str, Any]:
        """
        Get yt-dlp compatible search options.
        
        Returns:
            Dict[str, Any]: Options for yt-dlp search
        """
        options = {}
        
        # Add date filtering
        if self._config.upload_date != "any":
            options['dateafter'] = self._config.upload_date
        
        # Add duration filtering
        filter_config = self._config.filter_config
        if filter_config.min_duration or filter_config.max_duration:
            duration_range = []
            if filter_config.min_duration:
                duration_range.append(str(filter_config.min_duration))
            else:
                duration_range.append('')
            
            if filter_config.max_duration:
                duration_range.append(str(filter_config.max_duration))
            
            if duration_range:
                options['match_filter'] = f"duration >= {filter_config.min_duration or 0} & duration <= {filter_config.max_duration or 999999}"
        
        return options 