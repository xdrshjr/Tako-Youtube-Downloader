"""
YouTube Downloader - A high-quality Python script for downloading YouTube videos.

This package provides a modular and extensible solution for downloading YouTube videos
with proper error handling, configuration management, and logging.
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"

from .core.validator import URLValidator
from .core.downloader import VideoDownloader
from .core.config import ConfigManager

__all__ = ["URLValidator", "VideoDownloader", "ConfigManager"] 