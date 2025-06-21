"""
Progress tracking module for YouTube Downloader.

This module provides real-time progress tracking, ETA calculation,
speed display, and batch progress management.
"""

import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any, List
from contextlib import contextmanager


@dataclass
class ProgressInfo:
    """
    Progress information data class.
    
    Contains current progress state and calculated metrics.
    """
    downloaded_bytes: int
    total_bytes: Optional[int]
    speed: Optional[float]  # bytes per second
    eta: Optional[float]    # seconds remaining
    
    @property
    def percentage(self) -> float:
        """Calculate download percentage."""
        if not self.total_bytes or self.total_bytes == 0:
            return 0.0
        return (self.downloaded_bytes / self.total_bytes) * 100.0
    
    @property
    def speed_human_readable(self) -> str:
        """Get human readable speed string."""
        if not self.speed:
            return "Unknown"
        return ProgressTracker._format_size(self.speed) + "/s"
    
    @property
    def eta_human_readable(self) -> str:
        """Get human readable ETA string."""
        if not self.eta:
            return "Unknown"
        return ProgressTracker._format_time(int(self.eta))
    
    @property
    def downloaded_human_readable(self) -> str:
        """Get human readable downloaded size."""
        return ProgressTracker._format_size(self.downloaded_bytes)
    
    @property
    def total_human_readable(self) -> str:
        """Get human readable total size."""
        if not self.total_bytes:
            return "Unknown"
        return ProgressTracker._format_size(self.total_bytes)


class ProgressTracker:
    """
    Real-time progress tracker for download operations.
    
    Features:
    - Real-time progress updates
    - ETA calculation
    - Speed calculation
    - Human readable formatting
    - Context manager support
    """
    
    def __init__(self, callback: Callable[[ProgressInfo], None]):
        """
        Initialize progress tracker.
        
        Args:
            callback: Function to call with progress updates
        """
        self.callback = callback
        self.start_time: Optional[datetime] = None
        self.is_active = False
        
        # Internal state for calculations
        self._last_update_time: Optional[float] = None
        self._last_downloaded = 0
    
    def start(self):
        """Start progress tracking."""
        self.start_time = datetime.now()
        self.is_active = True
        self._last_update_time = None
        self._last_downloaded = 0
    
    def stop(self):
        """Stop progress tracking."""
        self.is_active = False
    
    def reset(self):
        """Reset tracker state."""
        self.start_time = None
        self.is_active = False
        self._last_update_time = None
        self._last_downloaded = 0
    
    def update(self, progress_data: Dict[str, Any]):
        """
        Update progress with data from yt-dlp.
        
        Args:
            progress_data: Progress data dictionary from yt-dlp
        """
        if not self.is_active:
            return
        
        # Extract basic information
        downloaded = progress_data.get('downloaded_bytes', 0)
        total = progress_data.get('total_bytes')
        speed = progress_data.get('speed')
        eta = progress_data.get('eta')
        
        # Calculate speed if not provided
        current_time = time.time()
        if speed is None and self._last_update_time is not None:
            time_diff = current_time - self._last_update_time
            bytes_diff = downloaded - self._last_downloaded
            if time_diff > 0:
                speed = bytes_diff / time_diff
        
        # Calculate ETA if not provided
        if eta is None and speed is not None and total is not None and speed > 0:
            remaining_bytes = total - downloaded
            eta = remaining_bytes / speed
        
        # Update internal state
        self._last_update_time = current_time
        self._last_downloaded = downloaded
        
        # Create progress info
        progress_info = ProgressInfo(
            downloaded_bytes=downloaded,
            total_bytes=total,
            speed=speed,
            eta=eta
        )
        
        # Call the callback
        self.callback(progress_info)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    @staticmethod
    def _format_size(bytes_size: float) -> str:
        """
        Format bytes to human readable string.
        
        Args:
            bytes_size: Size in bytes
            
        Returns:
            Human readable size string
        """
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024**2:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024**3:
            return f"{bytes_size / (1024**2):.1f} MB"
        elif bytes_size < 1024**4:
            return f"{bytes_size / (1024**3):.1f} GB"
        else:
            return f"{bytes_size / (1024**4):.1f} TB"
    
    @staticmethod
    def _format_time(seconds: int) -> str:
        """
        Format seconds to human readable time string.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Human readable time string (HH:MM:SS or MM:SS)
        """
        if seconds < 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class BatchProgressTracker:
    """
    Progress tracker for batch downloads.
    
    Manages multiple download progress trackers and provides
    overall progress statistics.
    """
    
    def __init__(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Initialize batch progress tracker.
        
        Args:
            callback: Function to call with batch progress updates
        """
        self.callback = callback
        self.item_trackers: Dict[str, ProgressTracker] = {}
        self.item_progress: Dict[str, ProgressInfo] = {}
        self.completed_items = 0
        self.start_time: Optional[datetime] = None
    
    @property
    def total_items(self) -> int:
        """Get total number of items."""
        return len(self.item_trackers)
    
    @property
    def is_complete(self) -> bool:
        """Check if all items are completed."""
        return self.completed_items >= self.total_items
    
    @property
    def completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100.0
    
    def add_item(self, item_id: str) -> ProgressTracker:
        """
        Add an item to track.
        
        Args:
            item_id: Unique identifier for the item
            
        Returns:
            ProgressTracker instance for the item
        """
        def item_callback(progress_info: ProgressInfo):
            self._on_item_progress(item_id, progress_info)
        
        tracker = ProgressTracker(item_callback)
        self.item_trackers[item_id] = tracker
        
        if self.start_time is None:
            self.start_time = datetime.now()
        
        return tracker
    
    def _on_item_progress(self, item_id: str, progress_info: ProgressInfo):
        """
        Handle progress update from individual item.
        
        Args:
            item_id: Item identifier
            progress_info: Progress information
        """
        self.item_progress[item_id] = progress_info
        
        # Check if item is complete
        if progress_info.percentage >= 100.0:
            self._on_item_complete(item_id)
        
        # Update overall progress
        self._update_batch_progress()
    
    def _on_item_complete(self, item_id: str):
        """
        Handle item completion.
        
        Args:
            item_id: Completed item identifier
        """
        if item_id not in [item for item in self.item_progress if self.item_progress[item].percentage >= 100.0]:
            self.completed_items += 1
        
        self._update_batch_progress()
    
    def _update_batch_progress(self):
        """Update and broadcast batch progress."""
        overall_progress = self.get_overall_progress()
        statistics = self.get_statistics()
        
        batch_info = {
            'overall_progress': overall_progress,
            'statistics': statistics,
            'is_complete': self.is_complete
        }
        
        self.callback(batch_info)
    
    def get_overall_progress(self) -> ProgressInfo:
        """
        Calculate overall progress across all items.
        
        Returns:
            ProgressInfo representing overall progress
        """
        if not self.item_progress:
            return ProgressInfo(0, 0, 0, None)
        
        total_downloaded = 0
        total_size = 0
        total_speed = 0
        active_items = 0
        
        for progress in self.item_progress.values():
            total_downloaded += progress.downloaded_bytes
            if progress.total_bytes:
                total_size += progress.total_bytes
            if progress.speed:
                total_speed += progress.speed
                active_items += 1
        
        # Calculate overall ETA
        overall_eta = None
        if total_speed > 0 and total_size > 0:
            remaining_bytes = total_size - total_downloaded
            if remaining_bytes > 0:
                overall_eta = remaining_bytes / total_speed
        
        # Average speed
        avg_speed = total_speed / active_items if active_items > 0 else None
        
        return ProgressInfo(
            downloaded_bytes=total_downloaded,
            total_bytes=total_size if total_size > 0 else None,
            speed=avg_speed,
            eta=overall_eta
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed batch statistics.
        
        Returns:
            Dictionary with batch statistics
        """
        overall_progress = self.get_overall_progress()
        
        # Calculate elapsed time
        elapsed = None
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
        
        # Count items by status
        active_items = sum(1 for p in self.item_progress.values() 
                          if 0 < p.percentage < 100)
        pending_items = self.total_items - len(self.item_progress)
        
        return {
            'total_items': self.total_items,
            'completed_items': self.completed_items,
            'active_items': active_items,
            'pending_items': pending_items,
            'total_downloaded': overall_progress.downloaded_bytes,
            'total_size': overall_progress.total_bytes,
            'average_speed': overall_progress.speed,
            'elapsed_time': elapsed,
            'completion_percentage': self.completion_percentage
        }
    
    def reset(self):
        """Reset batch tracker state."""
        self.item_trackers.clear()
        self.item_progress.clear()
        self.completed_items = 0
        self.start_time = None


class ConsoleProgressDisplay:
    """
    Console-based progress display.
    
    Provides formatted console output for progress tracking.
    """
    
    def __init__(self, show_speed: bool = True, show_eta: bool = True):
        """
        Initialize console progress display.
        
        Args:
            show_speed: Whether to show download speed
            show_eta: Whether to show ETA
        """
        self.show_speed = show_speed
        self.show_eta = show_eta
        self._last_line_length = 0
    
    def update(self, progress_info: ProgressInfo, prefix: str = ""):
        """
        Update console display with progress information.
        
        Args:
            progress_info: Progress information to display
            prefix: Optional prefix for the progress line
        """
        # Build progress bar
        bar_length = 30
        if progress_info.total_bytes:
            filled_length = int(bar_length * progress_info.percentage / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            percentage_str = f"{progress_info.percentage:5.1f}%"
        else:
            bar = '█' * (int(time.time()) % bar_length) + '░' * (bar_length - (int(time.time()) % bar_length))
            percentage_str = " ?.?%"
        
        # Build size information
        if progress_info.total_bytes:
            size_info = f"{progress_info.downloaded_human_readable}/{progress_info.total_human_readable}"
        else:
            size_info = progress_info.downloaded_human_readable
        
        # Build additional info
        additional_info = []
        if self.show_speed and progress_info.speed:
            additional_info.append(f"Speed: {progress_info.speed_human_readable}")
        if self.show_eta and progress_info.eta:
            additional_info.append(f"ETA: {progress_info.eta_human_readable}")
        
        # Combine all parts
        parts = [prefix] if prefix else []
        parts.extend([
            f"[{bar}]",
            percentage_str,
            size_info
        ])
        parts.extend(additional_info)
        
        line = " ".join(parts)
        
        # Clear previous line and print new one
        print("\r" + " " * self._last_line_length, end="")
        print(f"\r{line}", end="", flush=True)
        self._last_line_length = len(line)
    
    def finish(self, message: str = "Complete!"):
        """
        Finish progress display with final message.
        
        Args:
            message: Final completion message
        """
        print(f"\r{message}")
        self._last_line_length = 0
    
    def clear(self):
        """Clear the current progress line."""
        print("\r" + " " * self._last_line_length + "\r", end="", flush=True)
        self._last_line_length = 0 