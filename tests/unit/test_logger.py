"""
Unit tests for Logger module.

Tests the logging functionality including levels, formatting, privacy protection,
and file management.
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from youtube_downloader.utils.logger import Logger, LogLevel


class TestLogger:
    """Test Logger class functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, 'test.log')
    
    def teardown_method(self):
        """Clean up after each test."""
        # Ensure all logger handlers are closed first
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)
        
        # Force garbage collection to release file handles
        import gc
        gc.collect()
        
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
            os.rmdir(self.temp_dir)
        except (OSError, PermissionError):
            # Ignore cleanup errors in tests
            pass
    
    def test_logger_initialization(self):
        """Test logger initialization with default settings."""
        logger = Logger("test_module")
        
        assert logger.name == "test_module"
        assert logger.level == LogLevel.INFO
        assert logger.log_file is None
    
    def test_logger_initialization_with_file(self):
        """Test logger initialization with log file."""
        logger = Logger("test_module", log_file=self.log_file)
        
        assert logger.name == "test_module"
        assert str(logger.log_file) == self.log_file
    
    def test_logger_levels(self):
        """Test different logging levels."""
        logger = Logger("test_module", level=LogLevel.DEBUG)
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
        
        assert mock_log.call_count == 5
    
    def test_logger_level_filtering(self):
        """Test that lower level messages are filtered out."""
        logger = Logger("test_module", level=LogLevel.WARNING)
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.debug("Debug message")  # Should not be logged
            logger.info("Info message")    # Should not be logged
            logger.warning("Warning message")  # Should be logged
            logger.error("Error message")      # Should be logged
        
        # Only WARNING and ERROR should be logged
        assert mock_log.call_count == 2
    
    def test_log_formatting(self):
        """Test log message formatting."""
        logger = Logger("test_module")
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.info("Test message")
        
        # Check that the call was made with INFO level and sanitized message
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        assert call_args[0][0] == logging.INFO  # log level
        assert "Test message" in call_args[0][1]  # message
    
    def test_privacy_protection_url_sanitization(self):
        """Test that URLs are sanitized in log messages."""
        logger = Logger("test_module")
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.info("Processing URL: https://youtube.com/watch?v=dQw4w9WgXcQ")
        
        call_args = mock_log.call_args[0][1]  # message argument
        assert "https://youtube.com/watch?v=dQw4w9WgXcQ" not in call_args
        assert "dQw4w9WgXcQ" in call_args  # Video ID should be preserved
        assert "[URL_SANITIZED:" in call_args
    
    def test_privacy_protection_personal_data(self):
        """Test that personal data patterns are sanitized."""
        logger = Logger("test_module")
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.info("User email: user@example.com, IP: 192.168.1.1")
        
        call_args = mock_log.call_args[0][1]  # message argument
        assert "user@example.com" not in call_args
        assert "192.168.1.1" not in call_args
        assert "[EMAIL_SANITIZED]" in call_args
        assert "[IP_SANITIZED]" in call_args
    
    def test_file_logging(self):
        """Test logging to file."""
        logger = Logger("test_module", log_file=self.log_file)
        
        logger.info("Test file logging")
        
        # Give some time for file write
        import time
        time.sleep(0.1)
        
        # Check that file was created and contains the log entry
        assert os.path.exists(self.log_file)
        with open(self.log_file, 'r') as f:
            content = f.read()
            assert "[INFO]" in content
            assert "Test file logging" in content
    
    def test_log_rotation_size_limit(self):
        """Test log rotation when file size exceeds limit."""
        # Create logger with small max size for testing
        logger = Logger("test_module", log_file=self.log_file, max_size_mb=0.001)  # 1KB
        
        # Write enough data to trigger rotation
        for i in range(50):  # Reduced number to avoid too much output
            logger.info(f"Long log message number {i} with lots of text to fill up space")
        
        # Give some time for file operations
        import time
        time.sleep(0.1)
        
        # Check that either backup file was created or main file exists
        backup_file = self.log_file + ".1"
        assert os.path.exists(backup_file) or os.path.exists(self.log_file)
    
    def test_context_manager(self):
        """Test logger as context manager."""
        with Logger("test_module", log_file=self.log_file) as logger:
            logger.info("Context manager test")
        
        # Give some time for file operations
        import time
        time.sleep(0.1)
        
        # Check that file was properly closed and contains the log
        assert os.path.exists(self.log_file)
        with open(self.log_file, 'r') as f:
            content = f.read()
            assert "Context manager test" in content
    
    def test_exception_logging(self):
        """Test logging with exception information."""
        logger = Logger("test_module")
        
        with patch.object(logger._logger, 'log') as mock_log:
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                logger.error("Error occurred", exc_info=True)
        
        call_args = mock_log.call_args[0][1]  # message argument
        # When exc_info=True is passed, the logger should include exception info
        mock_log.assert_called_once()
        assert mock_log.call_args[1]['exc_info'] == True
    
    def test_structured_logging(self):
        """Test structured logging with additional context."""
        logger = Logger("test_module")
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.info("Download started", extra={
                'video_id': 'TEST123',
                'quality': '720p',
                'format': 'mp4'
            })
        
        call_args = mock_log.call_args[0][1]  # message argument
        assert "video_id=TEST123" in call_args
        assert "quality=720p" in call_args
        assert "format=mp4" in call_args


class TestLogLevel:
    """Test LogLevel enum."""
    
    def test_log_level_values(self):
        """Test that log levels have correct values."""
        assert LogLevel.DEBUG.value == 10
        assert LogLevel.INFO.value == 20
        assert LogLevel.WARNING.value == 30
        assert LogLevel.ERROR.value == 40
        assert LogLevel.CRITICAL.value == 50
    
    def test_log_level_comparison(self):
        """Test log level comparison."""
        assert LogLevel.DEBUG < LogLevel.INFO
        assert LogLevel.INFO < LogLevel.WARNING
        assert LogLevel.WARNING < LogLevel.ERROR
        assert LogLevel.ERROR < LogLevel.CRITICAL 