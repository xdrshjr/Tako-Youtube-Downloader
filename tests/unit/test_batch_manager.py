"""
Unit tests for BatchDownloadManager module.

This module tests the batch download functionality including queue management,
concurrent downloads, progress tracking, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import threading
import time
from queue import Queue

from src.youtube_downloader.core import (
    BatchDownloadManager,
    BatchConfig,
    BatchProgress,
    VideoDownloadTask,
    BatchStatus,
    VideoDownloadStatus,
    BatchDownloadError,
    VideoDownloader,
    DownloadConfig,
    VideoSearchResult,
    DownloadResult
)


class TestBatchConfig(unittest.TestCase):
    """Test BatchConfig data class."""
    
    def test_default_config(self):
        """Test BatchConfig with default values."""
        config = BatchConfig()
        
        self.assertEqual(config.max_concurrent_downloads, 3)
        self.assertTrue(config.retry_failed_downloads)
        self.assertEqual(config.max_retry_attempts, 3)
        self.assertEqual(config.retry_delay, 2.0)
        self.assertFalse(config.stop_on_first_error)
        self.assertTrue(config.save_progress)
        self.assertIsNone(config.progress_file)
    
    def test_custom_config(self):
        """Test BatchConfig with custom values."""
        config = BatchConfig(
            max_concurrent_downloads=5,
            retry_failed_downloads=False,
            max_retry_attempts=1,
            retry_delay=1.0,
            stop_on_first_error=True,
            save_progress=False,
            progress_file="progress.json"
        )
        
        self.assertEqual(config.max_concurrent_downloads, 5)
        self.assertFalse(config.retry_failed_downloads)
        self.assertEqual(config.max_retry_attempts, 1)
        self.assertEqual(config.retry_delay, 1.0)
        self.assertTrue(config.stop_on_first_error)
        self.assertFalse(config.save_progress)
        self.assertEqual(config.progress_file, "progress.json")


class TestVideoDownloadTask(unittest.TestCase):
    """Test VideoDownloadTask data class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.video = VideoSearchResult(
            video_id="test123",
            title="Test Video",
            duration=300,
            uploader="Test Channel",
            upload_date="2023-01-01",
            view_count=1000
        )
        self.config = DownloadConfig()
        
    def test_task_creation(self):
        """Test VideoDownloadTask creation."""
        task = VideoDownloadTask(
            video=self.video,
            download_config=self.config,
            task_id="task_123"
        )
        
        self.assertEqual(task.video, self.video)
        self.assertEqual(task.download_config, self.config)
        self.assertEqual(task.task_id, "task_123")
        self.assertEqual(task.status, VideoDownloadStatus.WAITING)
        self.assertIsNone(task.result)
        self.assertEqual(task.progress, 0.0)
        self.assertEqual(task.retry_count, 0)
    
    def test_get_url(self):
        """Test task URL generation."""
        task = VideoDownloadTask(
            video=self.video,
            download_config=self.config,
            task_id="task_123"
        )
        
        expected_url = f"https://www.youtube.com/watch?v={self.video.video_id}"
        self.assertEqual(task.get_url(), expected_url)
    
    def test_get_duration(self):
        """Test task duration calculation."""
        task = VideoDownloadTask(
            video=self.video,
            download_config=self.config,
            task_id="task_123"
        )
        
        # No start/end time
        self.assertEqual(task.get_duration(), 0.0)
        
        # With start/end time
        task.start_time = 1000.0
        task.end_time = 1010.5
        self.assertEqual(task.get_duration(), 10.5)


class TestBatchProgress(unittest.TestCase):
    """Test BatchProgress data class."""
    
    def test_progress_creation(self):
        """Test BatchProgress creation."""
        progress = BatchProgress(total_videos=10)
        
        self.assertEqual(progress.total_videos, 10)
        self.assertEqual(progress.completed_videos, 0)
        self.assertEqual(progress.failed_videos, 0)
        self.assertEqual(progress.cancelled_videos, 0)
        self.assertEqual(progress.overall_progress, 0.0)
        self.assertEqual(progress.status, BatchStatus.IDLE)
    
    def test_get_remaining_videos(self):
        """Test remaining videos calculation."""
        progress = BatchProgress(
            total_videos=10,
            completed_videos=3,
            failed_videos=1,
            cancelled_videos=1
        )
        
        self.assertEqual(progress.get_remaining_videos(), 5)
    
    def test_get_success_rate(self):
        """Test success rate calculation."""
        # Empty batch
        progress = BatchProgress(total_videos=0)
        self.assertEqual(progress.get_success_rate(), 0.0)
        
        # Partial completion
        progress = BatchProgress(
            total_videos=10,
            completed_videos=7
        )
        self.assertEqual(progress.get_success_rate(), 70.0)


class TestBatchDownloadManager(unittest.TestCase):
    """Test BatchDownloadManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_downloader = Mock(spec=VideoDownloader)
        self.mock_downloader.config = DownloadConfig()
        
        self.batch_config = BatchConfig(
            max_concurrent_downloads=2,
            retry_failed_downloads=True,
            max_retry_attempts=2
        )
        
        self.manager = BatchDownloadManager(
            downloader=self.mock_downloader,
            batch_config=self.batch_config
        )
        
        # Create test videos
        self.test_videos = [
            VideoSearchResult(
                video_id=f"test{i}",
                title=f"Test Video {i}",
                duration=300,
                uploader="Test Channel",
                upload_date="2023-01-01",
                view_count=1000
            )
            for i in range(5)
        ]
    
    def test_manager_initialization(self):
        """Test BatchDownloadManager initialization."""
        self.assertEqual(self.manager.downloader, self.mock_downloader)
        self.assertEqual(self.manager.batch_config, self.batch_config)
        self.assertEqual(self.manager._status, BatchStatus.IDLE)
        self.assertFalse(self.manager._is_paused)
        self.assertFalse(self.manager._is_cancelled)
        self.assertEqual(self.manager.get_queue_size(), 0)
    
    def test_add_to_queue_empty_list(self):
        """Test adding empty video list to queue."""
        initial_size = self.manager.get_queue_size()
        self.manager.add_to_queue([])
        
        self.assertEqual(self.manager.get_queue_size(), initial_size)
    
    def test_add_to_queue_with_videos(self):
        """Test adding videos to queue."""
        self.manager.add_to_queue(self.test_videos[:3])
        
        self.assertEqual(self.manager.get_queue_size(), 3)
        self.assertEqual(self.manager._progress.total_videos, 3)
    
    def test_add_to_queue_multiple_times(self):
        """Test adding videos to queue multiple times."""
        self.manager.add_to_queue(self.test_videos[:2])
        self.manager.add_to_queue(self.test_videos[2:4])
        
        self.assertEqual(self.manager.get_queue_size(), 4)
        self.assertEqual(self.manager._progress.total_videos, 4)
    
    def test_get_progress(self):
        """Test getting current progress."""
        progress = self.manager.get_progress()
        
        self.assertIsInstance(progress, BatchProgress)
        self.assertEqual(progress.status, BatchStatus.IDLE)
    
    def test_set_progress_callback(self):
        """Test setting progress callback."""
        callback = Mock()
        self.manager.set_progress_callback(callback)
        
        self.assertEqual(self.manager._progress_callback, callback)
    
    def test_get_batch_summary(self):
        """Test getting batch summary."""
        self.manager.add_to_queue(self.test_videos[:3])
        
        summary = self.manager.get_batch_summary()
        
        self.assertIn('status', summary)
        self.assertIn('total_videos', summary)
        self.assertIn('completed', summary)
        self.assertIn('failed', summary)
        self.assertIn('success_rate', summary)
        self.assertEqual(summary['total_videos'], 3)
    
    @patch('threading.Event')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_start_batch_download_empty_queue(self, mock_executor, mock_event):
        """Test starting batch download with empty queue."""
        # Should log warning and return without starting
        self.manager.start_batch_download()
        
        # Executor should not be created for empty queue
        mock_executor.assert_not_called()
    
    @patch('threading.Event')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_start_batch_download_already_running(self, mock_executor, mock_event):
        """Test starting batch download when already running."""
        self.manager._status = BatchStatus.RUNNING
        
        self.manager.start_batch_download()
        
        # Should not create new executor
        mock_executor.assert_not_called()
    
    def test_pause_download_not_running(self):
        """Test pausing download when not running."""
        self.manager.pause_download()
        
        # Status should remain unchanged
        self.assertEqual(self.manager._status, BatchStatus.IDLE)
    
    def test_pause_download_running(self):
        """Test pausing download when running."""
        self.manager._status = BatchStatus.RUNNING
        
        self.manager.pause_download()
        
        self.assertTrue(self.manager._is_paused)
        self.assertEqual(self.manager._status, BatchStatus.PAUSED)
    
    def test_resume_download_not_paused(self):
        """Test resuming download when not paused."""
        self.manager.resume_download()
        
        # Status should remain unchanged
        self.assertEqual(self.manager._status, BatchStatus.IDLE)
    
    def test_resume_download_paused(self):
        """Test resuming download when paused."""
        self.manager._status = BatchStatus.PAUSED
        self.manager._is_paused = True
        
        self.manager.resume_download()
        
        self.assertFalse(self.manager._is_paused)
        self.assertEqual(self.manager._status, BatchStatus.RUNNING)
    
    def test_cancel_download_not_active(self):
        """Test cancelling download when not active."""
        self.manager.cancel_download()
        
        # Status should remain unchanged
        self.assertEqual(self.manager._status, BatchStatus.IDLE)
    
    def test_cancel_download_running(self):
        """Test cancelling download when running."""
        self.manager._status = BatchStatus.RUNNING
        self.manager.add_to_queue(self.test_videos[:2])
        
        self.manager.cancel_download()
        
        self.assertTrue(self.manager._is_cancelled)
        self.assertEqual(self.manager._status, BatchStatus.CANCELLED)
        self.mock_downloader.cancel_download.assert_called_once()
    
    def test_get_completed_tasks(self):
        """Test getting completed tasks."""
        # Add some mock completed tasks
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        self.manager._completed_tasks.append(task)
        
        completed = self.manager.get_completed_tasks()
        
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0], task)
    
    def test_get_failed_tasks(self):
        """Test getting failed tasks."""
        # Add some mock failed tasks
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        task.status = VideoDownloadStatus.FAILED
        self.manager._failed_tasks.append(task)
        
        failed = self.manager.get_failed_tasks()
        
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0], task)
    
    @patch('time.time')
    def test_download_single_video_success(self, mock_time):
        """Test successful single video download."""
        mock_time.return_value = 1000.0
        
        # Create a task
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        
        # Mock successful download
        success_result = DownloadResult(
            success=True,
            video_info=None,
            output_path="/test/path.mp4"
        )
        self.mock_downloader.download_video.return_value = success_result
        
        # Execute download
        result_task = self.manager._download_single_video(task)
        
        self.assertEqual(result_task.status, VideoDownloadStatus.COMPLETED)
        self.assertEqual(result_task.result, success_result)
        self.mock_downloader.download_video.assert_called_once()
    
    @patch('time.time')
    def test_download_single_video_failure(self, mock_time):
        """Test failed single video download."""
        mock_time.return_value = 1000.0
        
        # Create a task
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        
        # Mock failed download
        failure_result = DownloadResult(
            success=False,
            error_message="Download failed"
        )
        self.mock_downloader.download_video.return_value = failure_result
        
        # Execute download
        result_task = self.manager._download_single_video(task)
        
        self.assertEqual(result_task.status, VideoDownloadStatus.FAILED)
        self.assertEqual(result_task.error_message, "Download failed")
    
    @patch('time.time')
    def test_download_single_video_exception(self, mock_time):
        """Test single video download with exception."""
        mock_time.return_value = 1000.0
        
        # Create a task
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        
        # Mock download exception
        self.mock_downloader.download_video.side_effect = Exception("Network error")
        
        # Execute download
        result_task = self.manager._download_single_video(task)
        
        self.assertEqual(result_task.status, VideoDownloadStatus.FAILED)
        self.assertEqual(result_task.error_message, "Network error")
    
    def test_download_single_video_cancelled(self):
        """Test single video download when cancelled."""
        # Create a task
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        
        # Set cancelled state
        self.manager._is_cancelled = True
        
        # Execute download
        result_task = self.manager._download_single_video(task)
        
        self.assertEqual(result_task.status, VideoDownloadStatus.CANCELLED)
        self.mock_downloader.download_video.assert_not_called()
    
    def test_process_completed_task_success(self):
        """Test processing successfully completed task."""
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        task.status = VideoDownloadStatus.COMPLETED
        
        # Add to active tasks first
        self.manager._active_tasks[task.task_id] = task
        
        initial_completed = self.manager._progress.completed_videos
        self.manager._process_completed_task(task)
        
        self.assertEqual(self.manager._progress.completed_videos, initial_completed + 1)
        self.assertNotIn(task.task_id, self.manager._active_tasks)
        self.assertIn(task, self.manager._completed_tasks)
    
    def test_process_completed_task_failed_no_retry(self):
        """Test processing failed task without retry."""
        self.batch_config.retry_failed_downloads = False
        
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        task.status = VideoDownloadStatus.FAILED
        
        # Add to active tasks first
        self.manager._active_tasks[task.task_id] = task
        
        initial_failed = self.manager._progress.failed_videos
        self.manager._process_completed_task(task)
        
        self.assertEqual(self.manager._progress.failed_videos, initial_failed + 1)
        self.assertIn(task, self.manager._failed_tasks)
    
    @patch('threading.Timer')
    def test_process_completed_task_failed_with_retry(self, mock_timer):
        """Test processing failed task with retry."""
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        task.status = VideoDownloadStatus.FAILED
        task.retry_count = 0
        
        # Add to active tasks first
        self.manager._active_tasks[task.task_id] = task
        
        self.manager._process_completed_task(task)
        
        # Should set up retry
        self.assertEqual(task.retry_count, 1)
        self.assertEqual(task.status, VideoDownloadStatus.WAITING)
        mock_timer.assert_called_once()
    
    def test_process_completed_task_max_retries_exceeded(self):
        """Test processing failed task when max retries exceeded."""
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        task.status = VideoDownloadStatus.FAILED
        task.retry_count = self.batch_config.max_retry_attempts
        
        # Add to active tasks first
        self.manager._active_tasks[task.task_id] = task
        
        initial_failed = self.manager._progress.failed_videos
        self.manager._process_completed_task(task)
        
        self.assertEqual(self.manager._progress.failed_videos, initial_failed + 1)
        self.assertIn(task, self.manager._failed_tasks)
    
    def test_process_completed_task_cancelled(self):
        """Test processing cancelled task."""
        task = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="test_task"
        )
        task.status = VideoDownloadStatus.CANCELLED
        
        # Add to active tasks first
        self.manager._active_tasks[task.task_id] = task
        
        initial_cancelled = self.manager._progress.cancelled_videos
        self.manager._process_completed_task(task)
        
        self.assertEqual(self.manager._progress.cancelled_videos, initial_cancelled + 1)
        self.assertIn(task, self.manager._completed_tasks)
    
    def test_update_progress_calculations(self):
        """Test progress update calculations."""
        # Set up some progress state
        self.manager._progress.total_videos = 10
        self.manager._progress.completed_videos = 3
        self.manager._progress.failed_videos = 1
        self.manager._progress.cancelled_videos = 1
        
        # Add some active downloads with progress
        task1 = VideoDownloadTask(
            video=self.test_videos[0],
            download_config=self.mock_downloader.config,
            task_id="task1"
        )
        task2 = VideoDownloadTask(
            video=self.test_videos[1],
            download_config=self.mock_downloader.config,
            task_id="task2"
        )
        
        self.manager._active_tasks["task1"] = task1
        self.manager._active_tasks["task2"] = task2
        self.manager._task_progress["task1"] = 0.5  # 50% progress
        self.manager._task_progress["task2"] = 0.3  # 30% progress
        
        self.manager._update_progress()
        
        # Check calculations
        # completed + failed + cancelled = 5
        # active progress = 0.5 + 0.3 = 0.8
        # overall = (5 + 0.8) / 10 * 100 = 58%
        expected_progress = (5 + 0.8) / 10 * 100
        self.assertAlmostEqual(self.manager._progress.overall_progress, expected_progress, places=1)
        self.assertEqual(self.manager._progress.active_downloads, 2)


if __name__ == '__main__':
    unittest.main() 