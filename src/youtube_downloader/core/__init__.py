"""
Core modules for YouTube Downloader.

This package contains the core business logic components:
- URLValidator: Validates and processes YouTube URLs
- VideoDownloader: Handles video downloading functionality
- ConfigManager: Manages application configuration
- SearchEngine: Provides YouTube video search functionality
- VideoFilter: Filters search results based on criteria
- SearchConfigManager: Manages search configuration
- BatchDownloadManager: Manages batch download operations
"""

from .validator import URLValidator
from .downloader import VideoDownloader, DownloadResult, VideoInfo
from .config import ConfigManager, DownloadConfig
from .search_engine import SearchEngine, SearchError, NetworkSearchError, YouTubeSearchError
from .video_filter import VideoFilter, VideoSearchResult
from .search_config import SearchConfig, FilterConfig, SearchConfigManager
from .batch_manager import (
    BatchDownloadManager,
    BatchConfig,
    BatchProgress,
    VideoDownloadTask,
    BatchStatus,
    VideoDownloadStatus,
    BatchDownloadError
)

__all__ = [
    "URLValidator", 
    "VideoDownloader",
    "DownloadResult",
    "VideoInfo", 
    "ConfigManager",
    "DownloadConfig",
    "SearchEngine",
    "SearchError",
    "NetworkSearchError", 
    "YouTubeSearchError",
    "VideoFilter",
    "VideoSearchResult",
    "SearchConfig",
    "FilterConfig",
    "SearchConfigManager",
    "BatchDownloadManager",
    "BatchConfig",
    "BatchProgress",
    "VideoDownloadTask",
    "BatchStatus",
    "VideoDownloadStatus",
    "BatchDownloadError"
] 