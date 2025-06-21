"""
Unit tests for ProgressTracker module.

Tests the progress tracking functionality including real-time updates,
ETA calculation, speed display, and batch progress tracking.
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from youtube_downloader.utils.progress import ProgressTracker, ProgressInfo, BatchProgressTracker


class TestProgressInfo:
    """Test ProgressInfo data class."""
    
    def test_progress_info_initialization(self):
        """Test ProgressInfo initialization."""
        info = ProgressInfo(
            downloaded_bytes=1024,
            total_bytes=2048,
            speed=512,
            eta=60
        )
        
        assert info.downloaded_bytes == 1024
        assert info.total_bytes == 2048
        assert info.speed == 512
        assert info.eta == 60
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        info = ProgressInfo(
            downloaded_bytes=1024,
            total_bytes=2048,
            speed=512,
            eta=60
        )
        
        assert info.percentage == 50.0
    
    def test_progress_percentage_unknown_total(self):
        """Test progress percentage when total is unknown."""
        info = ProgressInfo(
            downloaded_bytes=1024,
            total_bytes=None,
            speed=512,
            eta=None
        )
        
        assert info.percentage == 0.0
    
    def test_speed_human_readable(self):
        """Test human readable speed formatting."""
        info = ProgressInfo(
            downloaded_bytes=1024,
            total_bytes=2048,
            speed=1536,  # 1.5 KB/s
            eta=60
        )
        
        assert info.speed_human_readable == "1.5 KB/s"
    
    def test_eta_human_readable(self):
        """Test human readable ETA formatting."""
        info = ProgressInfo(
            downloaded_bytes=1024,
            total_bytes=2048,
            speed=512,
            eta=90  # 1 minute 30 seconds
        )
        
        assert info.eta_human_readable == "01:30"
    
    def test_size_human_readable(self):
        """Test human readable size formatting."""
        info = ProgressInfo(
            downloaded_bytes=1536,  # 1.5 KB
            total_bytes=1572864,    # 1.5 MB
            speed=512,
            eta=60
        )
        
        assert info.downloaded_human_readable == "1.5 KB"
        assert info.total_human_readable == "1.5 MB"


class TestProgressTracker:
    """Test ProgressTracker class functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.callback = Mock()
        self.tracker = ProgressTracker(self.callback)
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.callback == self.callback
        assert self.tracker.start_time is None
        assert self.tracker.is_active == False
    
    def test_start_tracking(self):
        """Test starting progress tracking."""
        self.tracker.start()
        
        assert self.tracker.is_active == True
        assert self.tracker.start_time is not None
        assert isinstance(self.tracker.start_time, datetime)
    
    def test_stop_tracking(self):
        """Test stopping progress tracking."""
        self.tracker.start()
        self.tracker.stop()
        
        assert self.tracker.is_active == False
    
    def test_update_progress(self):
        """Test progress update functionality."""
        self.tracker.start()
        
        # Simulate yt-dlp progress data
        progress_data = {
            'downloaded_bytes': 1024,
            'total_bytes': 2048,
            'speed': 512,
            'eta': 2
        }
        
        self.tracker.update(progress_data)
        
        # Check that callback was called
        self.callback.assert_called_once()
        
        # Check progress info
        call_args = self.callback.call_args[0][0]
        assert isinstance(call_args, ProgressInfo)
        assert call_args.downloaded_bytes == 1024
        assert call_args.total_bytes == 2048
        assert call_args.speed == 512
    
    def test_update_without_start(self):
        """Test that updates are ignored if tracking not started."""
        progress_data = {'downloaded_bytes': 1024}
        
        self.tracker.update(progress_data)
        
        # Callback should not be called
        self.callback.assert_not_called()
    
    def test_eta_calculation(self):
        """Test ETA calculation when not provided by yt-dlp."""
        self.tracker.start()
        
        progress_data = {
            'downloaded_bytes': 1024,
            'total_bytes': 2048,
            'speed': 512,
            # eta not provided
        }
        
        self.tracker.update(progress_data)
        
        call_args = self.callback.call_args[0][0]
        # ETA should be calculated: (2048 - 1024) / 512 = 2 seconds
        assert call_args.eta == 2
    
    def test_speed_calculation(self):
        """Test speed calculation when not provided by yt-dlp."""
        self.tracker.start()
        
        # First update
        with patch('time.time', return_value=1000.0):
            progress_data = {
                'downloaded_bytes': 512,
                'total_bytes': 2048
            }
            self.tracker.update(progress_data)
        
        # Second update after 1 second
        with patch('time.time', return_value=1001.0):
            progress_data = {
                'downloaded_bytes': 1024,
                'total_bytes': 2048
            }
            self.tracker.update(progress_data)
        
        # Speed should be calculated: (1024 - 512) / (1001 - 1000) = 512 bytes/s
        call_args = self.callback.call_args[0][0]
        assert call_args.speed == 512.0
    
    def test_progress_with_unknown_total(self):
        """Test progress tracking with unknown total size."""
        self.tracker.start()
        
        progress_data = {
            'downloaded_bytes': 1024,
            # total_bytes not provided
            'speed': 512
        }
        
        self.tracker.update(progress_data)
        
        call_args = self.callback.call_args[0][0]
        assert call_args.downloaded_bytes == 1024
        assert call_args.total_bytes is None
        assert call_args.percentage == 0.0
        assert call_args.eta is None
    
    def test_reset_tracking(self):
        """Test resetting tracker state."""
        self.tracker.start()
        progress_data = {'downloaded_bytes': 1024}
        self.tracker.update(progress_data)
        
        self.tracker.reset()
        
        assert self.tracker.is_active == False
        assert self.tracker.start_time is None
        assert self.tracker._last_update_time is None
        assert self.tracker._last_downloaded == 0
    
    def test_context_manager(self):
        """Test tracker as context manager."""
        with self.tracker:
            assert self.tracker.is_active == True
        
        assert self.tracker.is_active == False
    
    def test_format_size(self):
        """Test size formatting utility."""
        assert ProgressTracker._format_size(1024) == "1.0 KB"
        assert ProgressTracker._format_size(1048576) == "1.0 MB"
        assert ProgressTracker._format_size(1073741824) == "1.0 GB"
        assert ProgressTracker._format_size(512) == "512 B"
    
    def test_format_time(self):
        """Test time formatting utility."""
        assert ProgressTracker._format_time(30) == "00:30"
        assert ProgressTracker._format_time(90) == "01:30"
        assert ProgressTracker._format_time(3661) == "01:01:01"


class TestBatchProgressTracker:
    """Test BatchProgressTracker class functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.callback = Mock()
        self.batch_tracker = BatchProgressTracker(self.callback)
    
    def test_batch_initialization(self):
        """Test batch tracker initialization."""
        assert self.batch_tracker.callback == self.callback
        assert self.batch_tracker.total_items == 0
        assert self.batch_tracker.completed_items == 0
        assert len(self.batch_tracker.item_trackers) == 0
    
    def test_add_item(self):
        """Test adding items to batch tracker."""
        tracker1 = self.batch_tracker.add_item("item1")
        tracker2 = self.batch_tracker.add_item("item2")
        
        assert self.batch_tracker.total_items == 2
        assert "item1" in self.batch_tracker.item_trackers
        assert "item2" in self.batch_tracker.item_trackers
        assert isinstance(tracker1, ProgressTracker)
        assert isinstance(tracker2, ProgressTracker)
    
    def test_item_completion(self):
        """Test item completion tracking."""
        tracker1 = self.batch_tracker.add_item("item1")
        tracker2 = self.batch_tracker.add_item("item2")
        
        # Complete first item
        self.batch_tracker._on_item_complete("item1")
        
        assert self.batch_tracker.completed_items == 1
        assert self.batch_tracker.completion_percentage == 50.0
    
    def test_overall_progress_calculation(self):
        """Test overall progress calculation across items."""
        tracker1 = self.batch_tracker.add_item("item1")
        tracker2 = self.batch_tracker.add_item("item2")
        
        # Simulate progress on both items
        tracker1.start()
        tracker2.start()
        
        # Item 1: 50% complete
        progress_data1 = {
            'downloaded_bytes': 1024,
            'total_bytes': 2048,
            'speed': 512
        }
        tracker1.update(progress_data1)
        
        # Item 2: 25% complete
        progress_data2 = {
            'downloaded_bytes': 512,
            'total_bytes': 2048,
            'speed': 256
        }
        tracker2.update(progress_data2)
        
        # Overall progress should be (50% + 25%) / 2 = 37.5%
        overall_progress = self.batch_tracker.get_overall_progress()
        assert overall_progress.percentage == 37.5
    
    def test_batch_completion(self):
        """Test batch completion detection."""
        tracker1 = self.batch_tracker.add_item("item1")
        tracker2 = self.batch_tracker.add_item("item2")
        
        assert not self.batch_tracker.is_complete
        
        # Complete both items
        self.batch_tracker._on_item_complete("item1")
        self.batch_tracker._on_item_complete("item2")
        
        assert self.batch_tracker.is_complete
        assert self.batch_tracker.completion_percentage == 100.0
    
    def test_batch_statistics(self):
        """Test batch statistics calculation."""
        tracker1 = self.batch_tracker.add_item("item1")
        tracker2 = self.batch_tracker.add_item("item2")
        
        # Set up progress data
        tracker1.start()
        tracker2.start()
        
        progress_data1 = {
            'downloaded_bytes': 1024,
            'total_bytes': 2048,
            'speed': 512
        }
        tracker1.update(progress_data1)
        
        progress_data2 = {
            'downloaded_bytes': 512,
            'total_bytes': 1024,
            'speed': 256
        }
        tracker2.update(progress_data2)
        
        stats = self.batch_tracker.get_statistics()
        
        assert stats['total_items'] == 2
        assert stats['completed_items'] == 0
        assert stats['total_downloaded'] == 1536  # 1024 + 512
        assert stats['total_size'] == 3072  # 2048 + 1024
        assert stats['average_speed'] == 384  # (512 + 256) / 2
    
    def test_reset_batch(self):
        """Test resetting batch tracker."""
        tracker1 = self.batch_tracker.add_item("item1")
        self.batch_tracker._on_item_complete("item1")
        
        self.batch_tracker.reset()
        
        assert self.batch_tracker.total_items == 0
        assert self.batch_tracker.completed_items == 0
        assert len(self.batch_tracker.item_trackers) == 0 