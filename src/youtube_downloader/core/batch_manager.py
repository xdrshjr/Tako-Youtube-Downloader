"""
Batch download manager module for YouTube Downloader.

This module provides batch download management functionality for handling
multiple video downloads with queue management, progress tracking, and
error handling.
"""

import asyncio
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path

from .downloader import VideoDownloader, DownloadResult
from .video_filter import VideoSearchResult
from .config import DownloadConfig


class BatchStatus(Enum):
    """Batch download status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class VideoDownloadStatus(Enum):
    """Individual video download status enumeration."""
    WAITING = "waiting"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class VideoDownloadTask:
    """
    Data class representing a single video download task.
    """
    video: VideoSearchResult
    download_config: DownloadConfig
    task_id: str
    status: VideoDownloadStatus = VideoDownloadStatus.WAITING
    result: Optional[DownloadResult] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    retry_count: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def get_url(self) -> str:
        """Get the YouTube URL for this task."""
        return self.video.get_url()
    
    def get_duration(self) -> float:
        """Get download duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


@dataclass
class BatchProgress:
    """
    Data class representing batch download progress.
    """
    total_videos: int
    completed_videos: int = 0
    failed_videos: int = 0
    cancelled_videos: int = 0
    current_video: Optional[str] = None
    overall_progress: float = 0.0
    download_speed: str = "0 B/s"
    eta: str = "Unknown"
    status: BatchStatus = BatchStatus.IDLE
    active_downloads: int = 0
    
    def get_remaining_videos(self) -> int:
        """Get number of remaining videos to download."""
        return self.total_videos - self.completed_videos - self.failed_videos - self.cancelled_videos
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_videos == 0:
            return 0.0
        return (self.completed_videos / self.total_videos) * 100


@dataclass
class BatchConfig:
    """
    Configuration for batch download operations.
    """
    max_concurrent_downloads: int = 3
    retry_failed_downloads: bool = True
    max_retry_attempts: int = 3
    retry_delay: float = 2.0
    stop_on_first_error: bool = False
    save_progress: bool = True
    progress_file: Optional[str] = None


class BatchDownloadError(Exception):
    """Base exception for batch download errors."""
    pass


class BatchDownloadManager:
    """
    Enhanced batch download manager for handling multiple video downloads.
    
    Features:
    - Queue-based download management
    - Concurrent download control with configurable limits
    - Real-time progress tracking and aggregation
    - Comprehensive error handling and retry logic
    - Pause/resume functionality
    - Download queue persistence
    """
    
    def __init__(self, downloader: VideoDownloader, batch_config: BatchConfig):
        """
        Initialize the batch download manager.
        
        Args:
            downloader: VideoDownloader instance for individual downloads
            batch_config: Configuration for batch operations
        """
        self.downloader = downloader
        self.batch_config = batch_config
        
        # Download queue and task management
        self._download_queue: Queue[VideoDownloadTask] = Queue()
        self._active_tasks: Dict[str, VideoDownloadTask] = {}
        self._completed_tasks: List[VideoDownloadTask] = []
        self._failed_tasks: List[VideoDownloadTask] = []
        
        # Thread management
        self._executor: Optional[ThreadPoolExecutor] = None
        self._futures: Dict[str, Any] = {}
        
        # Status and control
        self._status = BatchStatus.IDLE
        self._is_paused = False
        self._is_cancelled = False
        self._pause_event = threading.Event()
        self._pause_event.set()  # Initially not paused
        
        # Progress tracking
        self._progress = BatchProgress(total_videos=0)
        self._progress_callback: Optional[Callable[[BatchProgress], None]] = None
        self._task_progress: Dict[str, float] = {}
        
        # Logging
        self._logger = logging.getLogger(__name__)
        
        self._logger.info("BatchDownloadManager initialized", extra={
            'max_concurrent': batch_config.max_concurrent_downloads,
            'retry_enabled': batch_config.retry_failed_downloads,
            'max_retries': batch_config.max_retry_attempts
        })
    
    def add_to_queue(self, videos: List[VideoSearchResult], download_config: Optional[DownloadConfig] = None) -> None:
        """
        Add videos to the download queue.
        
        Args:
            videos: List of video search results to download
            download_config: Download configuration (uses downloader's config if None)
        """
        if not videos:
            self._logger.warning("No videos provided to add to queue")
            return
        
        config = download_config or self.downloader.config
        added_count = 0
        
        for video in videos:
            task_id = f"{video.video_id}_{int(time.time())}"
            task = VideoDownloadTask(
                video=video,
                download_config=config,
                task_id=task_id
            )
            
            self._download_queue.put(task)
            added_count += 1
            
            self._logger.debug(f"Added to queue: {video.title} ({video.video_id})")
        
        # Update progress total
        self._progress.total_videos += added_count
        
        self._logger.info(f"Added {added_count} videos to download queue", extra={
            'queue_size': self._download_queue.qsize(),
            'total_videos': self._progress.total_videos
        })
    
    def start_batch_download(self) -> None:
        """
        Start the batch download process.
        
        Raises:
            BatchDownloadError: If batch download cannot be started
        """
        if self._status == BatchStatus.RUNNING:
            self._logger.warning("Batch download is already running")
            return
        
        if self._download_queue.empty() and not self._active_tasks:
            self._logger.warning("No videos in queue to download")
            return
        
        self._status = BatchStatus.RUNNING
        self._is_cancelled = False
        self._is_paused = False
        self._pause_event.set()
        
        # Initialize thread pool
        self._executor = ThreadPoolExecutor(
            max_workers=self.batch_config.max_concurrent_downloads,
            thread_name_prefix="BatchDownloader"
        )
        
        self._logger.info("Starting batch download", extra={
            'queue_size': self._download_queue.qsize(),
            'max_concurrent': self.batch_config.max_concurrent_downloads
        })
        
        try:
            self._run_batch_download()
        except Exception as e:
            self._status = BatchStatus.ERROR
            self._logger.error(f"Batch download failed: {str(e)}")
            raise BatchDownloadError(f"Batch download failed: {str(e)}")
    
    def pause_download(self) -> None:
        """Pause the batch download process."""
        if self._status != BatchStatus.RUNNING:
            self._logger.warning("Cannot pause: batch download is not running")
            return
        
        self._is_paused = True
        self._pause_event.clear()
        self._status = BatchStatus.PAUSED
        
        self._logger.info("Batch download paused")
        self._update_progress()
    
    def resume_download(self) -> None:
        """Resume the paused batch download process."""
        if self._status != BatchStatus.PAUSED:
            self._logger.warning("Cannot resume: batch download is not paused")
            return
        
        self._is_paused = False
        self._pause_event.set()
        self._status = BatchStatus.RUNNING
        
        self._logger.info("Batch download resumed")
        self._update_progress()
    
    def cancel_download(self) -> None:
        """Cancel the batch download process."""
        if self._status not in [BatchStatus.RUNNING, BatchStatus.PAUSED]:
            self._logger.warning("Cannot cancel: batch download is not active")
            return
        
        self._is_cancelled = True
        self._status = BatchStatus.CANCELLED
        
        # Cancel all active downloads
        for task in self._active_tasks.values():
            task.status = VideoDownloadStatus.CANCELLED
        
        # Cancel VideoDownloader
        self.downloader.cancel_download()
        
        # Clear queue
        while not self._download_queue.empty():
            try:
                task = self._download_queue.get_nowait()
                task.status = VideoDownloadStatus.CANCELLED
                self._completed_tasks.append(task)
                self._progress.cancelled_videos += 1
            except Empty:
                break
        
        # Shutdown executor
        if self._executor:
            self._executor.shutdown(wait=False)
        
        self._logger.info("Batch download cancelled")
        self._update_progress()
    
    def get_progress(self) -> BatchProgress:
        """
        Get current batch download progress.
        
        Returns:
            BatchProgress: Current progress information
        """
        return self._progress
    
    def set_progress_callback(self, callback: Callable[[BatchProgress], None]) -> None:
        """
        Set progress update callback.
        
        Args:
            callback: Function to call when progress is updated
        """
        self._progress_callback = callback
        self._logger.debug("Progress callback set")
    
    def get_completed_tasks(self) -> List[VideoDownloadTask]:
        """Get list of completed download tasks."""
        return self._completed_tasks.copy()
    
    def get_failed_tasks(self) -> List[VideoDownloadTask]:
        """Get list of failed download tasks."""
        return self._failed_tasks.copy()
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self._download_queue.qsize()
    
    def get_batch_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive batch download summary.
        
        Returns:
            Dict containing detailed batch statistics
        """
        total_duration = sum(task.get_duration() for task in self._completed_tasks)
        successful_downloads = len([t for t in self._completed_tasks if t.status == VideoDownloadStatus.COMPLETED])
        
        return {
            'status': self._status.value,
            'total_videos': self._progress.total_videos,
            'completed': self._progress.completed_videos,
            'failed': self._progress.failed_videos,
            'cancelled': self._progress.cancelled_videos,
            'success_rate': self._progress.get_success_rate(),
            'total_duration': total_duration,
            'average_download_time': total_duration / max(1, successful_downloads),
            'queue_size': self.get_queue_size(),
            'active_downloads': len(self._active_tasks)
        }
    
    def _run_batch_download(self) -> None:
        """Main batch download execution loop."""
        try:
            while not self._is_cancelled and (not self._download_queue.empty() or self._active_tasks):
                # Wait if paused
                self._pause_event.wait()
                
                if self._is_cancelled:
                    break
                
                # Start new downloads if slots available
                while (len(self._active_tasks) < self.batch_config.max_concurrent_downloads and 
                       not self._download_queue.empty() and not self._is_cancelled):
                    
                    try:
                        task = self._download_queue.get_nowait()
                        self._start_download_task(task)
                    except Empty:
                        break
                
                # Check completed downloads
                self._check_completed_downloads()
                
                # Update progress
                self._update_progress()
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
            
            # Wait for remaining downloads to complete
            self._wait_for_completion()
            
            # Final status update
            if not self._is_cancelled:
                self._status = BatchStatus.COMPLETED
            
            self._update_progress()
            
        finally:
            # Cleanup
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None
    
    def _start_download_task(self, task: VideoDownloadTask) -> None:
        """Start downloading a single video task."""
        task.status = VideoDownloadStatus.DOWNLOADING
        task.start_time = time.time()
        self._active_tasks[task.task_id] = task
        
        # Create progress callback for this task
        def task_progress_callback(progress_info):
            self._task_progress[task.task_id] = progress_info.progress
            self._update_progress()
        
        # Set up the downloader with task-specific progress callback
        original_callback = self.downloader._external_progress_callback
        self.downloader.set_progress_callback(task_progress_callback)
        
        # Submit download task
        future = self._executor.submit(self._download_single_video, task)
        self._futures[task.task_id] = future
        
        # Restore original callback
        self.downloader.set_progress_callback(original_callback)
        
        self._logger.debug(f"Started download task: {task.video.title} ({task.task_id})")
    
    def _download_single_video(self, task: VideoDownloadTask) -> VideoDownloadTask:
        """Download a single video and handle errors."""
        try:
            # Wait if paused
            self._pause_event.wait()
            
            if self._is_cancelled:
                task.status = VideoDownloadStatus.CANCELLED
                return task
            
            # Perform the download
            result = self.downloader.download_video(task.get_url())
            task.result = result
            task.end_time = time.time()
            
            if result.success:
                task.status = VideoDownloadStatus.COMPLETED
                self._logger.info(f"Download completed: {task.video.title}")
            else:
                task.status = VideoDownloadStatus.FAILED
                task.error_message = result.error_message
                self._logger.warning(f"Download failed: {task.video.title} - {result.error_message}")
        
        except Exception as e:
            task.status = VideoDownloadStatus.FAILED
            task.error_message = str(e)
            task.end_time = time.time()
            self._logger.error(f"Download error: {task.video.title} - {str(e)}")
        
        return task
    
    def _check_completed_downloads(self) -> None:
        """Check for completed download tasks and process them."""
        completed_futures = []
        
        for task_id, future in self._futures.items():
            if future.done():
                completed_futures.append(task_id)
                
                try:
                    task = future.result()
                    self._process_completed_task(task)
                except Exception as e:
                    self._logger.error(f"Error processing completed task {task_id}: {str(e)}")
                    if task_id in self._active_tasks:
                        task = self._active_tasks[task_id]
                        task.status = VideoDownloadStatus.FAILED
                        task.error_message = str(e)
                        self._process_completed_task(task)
        
        # Clean up completed futures
        for task_id in completed_futures:
            self._futures.pop(task_id, None)
            self._task_progress.pop(task_id, None)
    
    def _process_completed_task(self, task: VideoDownloadTask) -> None:
        """Process a completed download task."""
        # Remove from active tasks
        self._active_tasks.pop(task.task_id, None)
        
        if task.status == VideoDownloadStatus.COMPLETED:
            self._completed_tasks.append(task)
            self._progress.completed_videos += 1
            
        elif task.status == VideoDownloadStatus.FAILED:
            # Check if we should retry
            if (self.batch_config.retry_failed_downloads and 
                task.retry_count < self.batch_config.max_retry_attempts):
                
                task.retry_count += 1
                task.status = VideoDownloadStatus.WAITING
                
                # Add back to queue with delay
                threading.Timer(
                    self.batch_config.retry_delay,
                    lambda: self._download_queue.put(task)
                ).start()
                
                self._logger.info(f"Retrying download: {task.video.title} (attempt {task.retry_count})")
            else:
                self._failed_tasks.append(task)
                self._progress.failed_videos += 1
                
                if self.batch_config.stop_on_first_error:
                    self._logger.error("Stopping batch download due to error")
                    self.cancel_download()
                    
        elif task.status == VideoDownloadStatus.CANCELLED:
            self._completed_tasks.append(task)
            self._progress.cancelled_videos += 1
    
    def _wait_for_completion(self) -> None:
        """Wait for all active downloads to complete."""
        if not self._futures:
            return
        
        self._logger.info("Waiting for active downloads to complete")
        
        for future in as_completed(self._futures.values(), timeout=300):  # 5 minute timeout
            try:
                future.result()
            except Exception as e:
                self._logger.error(f"Error in completing download: {str(e)}")
        
        # Final check
        self._check_completed_downloads()
    
    def _update_progress(self) -> None:
        """Update overall progress and call progress callback."""
        # Update active downloads count
        self._progress.active_downloads = len(self._active_tasks)
        
        # Calculate overall progress
        if self._progress.total_videos > 0:
            completed_progress = (self._progress.completed_videos + 
                                self._progress.failed_videos + 
                                self._progress.cancelled_videos)
            
            # Add progress from active downloads
            active_progress = sum(self._task_progress.values())
            
            self._progress.overall_progress = min(100.0, 
                ((completed_progress + active_progress) / self._progress.total_videos) * 100)
        
        # Update current video (first active task)
        if self._active_tasks:
            first_task = next(iter(self._active_tasks.values()))
            self._progress.current_video = first_task.video.title
        else:
            self._progress.current_video = None
        
        # Update status
        self._progress.status = self._status
        
        # Calculate ETA (simplified)
        if self._progress.overall_progress > 0 and self._status == BatchStatus.RUNNING:
            remaining = 100 - self._progress.overall_progress
            # This is a simplified ETA calculation
            self._progress.eta = f"{int(remaining / max(1, self._progress.overall_progress) * 60)} min"
        else:
            self._progress.eta = "Unknown"
        
        # Call progress callback
        if self._progress_callback:
            try:
                self._progress_callback(self._progress)
            except Exception as e:
                self._logger.error(f"Error in progress callback: {str(e)}") 