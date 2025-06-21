"""
Logger module for YouTube Downloader.

This module provides structured logging with privacy protection, file rotation,
and configurable log levels.
"""

import logging
import os
import re
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Union
from logging.handlers import RotatingFileHandler
import traceback


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    
    def __lt__(self, other):
        if not isinstance(other, LogLevel):
            return NotImplemented
        return self.value < other.value


class Logger:
    """
    Custom logger with privacy protection and structured formatting.
    
    Features:
    - Privacy protection (URL and personal data sanitization)
    - Structured logging with context
    - File rotation support
    - Configurable log levels
    - Clean formatting
    """
    
    # Regex patterns for privacy protection
    URL_PATTERN = re.compile(r'https?://[^\s]+')
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    IP_PATTERN = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    
    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        log_file: Optional[Union[str, Path]] = None,
        max_size_mb: float = 10.0,
        backup_count: int = 5
    ):
        """
        Initialize logger.
        
        Args:
            name: Logger name (typically module name)
            level: Minimum log level
            log_file: Optional log file path
            max_size_mb: Maximum log file size in MB before rotation
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.level = level
        self.log_file = Path(log_file) if log_file else None
        self.max_size_mb = max_size_mb
        self.backup_count = backup_count
        
        # Initialize internal logger
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level.value)
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup log handlers (console and file)."""
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.level.value)
        self._logger.addHandler(console_handler)
        
        # File handler (if specified)
        if self.log_file:
            # Ensure directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler
            max_bytes = int(self.max_size_mb * 1024 * 1024)
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=max_bytes,
                backupCount=self.backup_count
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self.level.value)
            self._logger.addHandler(file_handler)
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize log message for privacy protection.
        
        Args:
            message: Original log message
            
        Returns:
            Sanitized message with sensitive data removed
        """
        # Sanitize URLs (keep video ID if it's a YouTube URL)
        def replace_url(match):
            url = match.group(0)
            if 'youtube.com/watch' in url or 'youtu.be/' in url:
                # Extract video ID
                video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
                if video_id_match:
                    return f"[URL_SANITIZED:{video_id_match.group(1)}]"
            return "[URL_SANITIZED]"
        
        message = self.URL_PATTERN.sub(replace_url, message)
        
        # Sanitize email addresses
        message = self.EMAIL_PATTERN.sub("[EMAIL_SANITIZED]", message)
        
        # Sanitize IP addresses
        message = self.IP_PATTERN.sub("[IP_SANITIZED]", message)
        
        return message
    
    def _format_extra_context(self, extra: Dict[str, Any]) -> str:
        """
        Format extra context information.
        
        Args:
            extra: Extra context dictionary
            
        Returns:
            Formatted context string
        """
        if not extra:
            return ""
        
        context_parts = []
        for key, value in extra.items():
            if isinstance(value, (str, int, float, bool)):
                context_parts.append(f"{key}={value}")
            else:
                context_parts.append(f"{key}={str(value)}")
        
        return " | " + " ".join(context_parts) if context_parts else ""
    
    def _write_log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """
        Write log entry with sanitization and formatting.
        
        Args:
            level: Log level
            message: Log message
            extra: Extra context information
            exc_info: Include exception information
        """
        if level < self.level:
            return
        
        # Sanitize message
        sanitized_message = self._sanitize_message(message)
        
        # Add extra context
        context = self._format_extra_context(extra or {})
        full_message = sanitized_message + context
        
        # Map to logging levels
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        
        # Log the message
        self._logger.log(level_map[level], full_message, exc_info=exc_info)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._write_log(LogLevel.DEBUG, message, extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._write_log(LogLevel.INFO, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._write_log(LogLevel.WARNING, message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log error message."""
        self._write_log(LogLevel.ERROR, message, extra, exc_info)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log critical message."""
        self._write_log(LogLevel.CRITICAL, message, extra, exc_info)
    
    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log exception with traceback."""
        self._write_log(LogLevel.ERROR, message, extra, exc_info=True)
    
    def log_download_start(self, video_id: str, title: str, url: str):
        """Log download start with structured information."""
        self.info("Download started", extra={
            'video_id': video_id,
            'title': title[:50] + '...' if len(title) > 50 else title,
            'action': 'download_start'
        })
    
    def log_download_progress(self, video_id: str, percentage: float, speed: Optional[float] = None):
        """Log download progress."""
        extra_info = {
            'video_id': video_id,
            'progress': f"{percentage:.1f}%",
            'action': 'download_progress'
        }
        if speed:
            extra_info['speed'] = f"{speed:.1f} KB/s"
        
        self.debug("Download progress", extra=extra_info)
    
    def log_download_complete(self, video_id: str, file_path: str, file_size: int, duration: float):
        """Log download completion."""
        self.info("Download completed", extra={
            'video_id': video_id,
            'file_size': f"{file_size / 1024 / 1024:.1f} MB",
            'duration': f"{duration:.1f}s",
            'action': 'download_complete'
        })
    
    def log_download_error(self, video_id: str, error: str, error_type: str = "unknown"):
        """Log download error."""
        self.error("Download failed", extra={
            'video_id': video_id,
            'error_type': error_type,
            'error': error[:200] + '...' if len(error) > 200 else error,
            'action': 'download_error'
        })
    
    def log_retry_attempt(self, video_id: str, attempt: int, max_attempts: int, error: str):
        """Log retry attempt."""
        self.warning("Retrying download", extra={
            'video_id': video_id,
            'attempt': f"{attempt}/{max_attempts}",
            'error': error[:100] + '...' if len(error) > 100 else error,
            'action': 'retry_attempt'
        })
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Flush and close handlers
        for handler in self._logger.handlers:
            handler.flush()
            if hasattr(handler, 'close'):
                handler.close()


# Global logger instance
_global_logger: Optional[Logger] = None


def get_logger(name: str = "youtube_downloader") -> Logger:
    """
    Get or create global logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    global _global_logger
    
    if _global_logger is None:
        # Default log file path
        log_dir = Path.cwd() / "logs"
        log_file = log_dir / "downloader.log"
        
        _global_logger = Logger(
            name=name,
            level=LogLevel.INFO,
            log_file=log_file
        )
    
    return _global_logger


def configure_logger(
    level: LogLevel = LogLevel.INFO,
    log_file: Optional[Union[str, Path]] = None,
    max_size_mb: float = 10.0,
    backup_count: int = 5
) -> Logger:
    """
    Configure global logger instance.
    
    Args:
        level: Minimum log level
        log_file: Optional log file path
        max_size_mb: Maximum log file size in MB
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    global _global_logger
    
    _global_logger = Logger(
        name="youtube_downloader",
        level=level,
        log_file=log_file,
        max_size_mb=max_size_mb,
        backup_count=backup_count
    )
    
    return _global_logger 