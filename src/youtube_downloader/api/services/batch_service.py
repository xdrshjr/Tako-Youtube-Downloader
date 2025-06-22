"""
Batch service for handling batch download operations.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional

from ...core import (
    BatchDownloadManager,
    BatchConfig,
    VideoDownloader,
    DownloadConfig,
    BatchProgress,
    BatchStatus,
    VideoSearchResult
)
from ..models.requests import BatchDownloadRequest
from ..models.responses import (
    BatchDownloadResponse,
    BatchProgressResponse,
    BatchTaskInfo,
    StatusEnum
)


class BatchService:
    """Service for handling batch download operations."""
    
    def __init__(self):
        """Initialize the batch service."""
        self.logger = logging.getLogger(__name__)
        self.active_batches: Dict[str, BatchDownloadManager] = {}
    
    def start_batch_download(self, request: BatchDownloadRequest) -> BatchDownloadResponse:
        """Start a batch download operation."""
        try:
            task_id = str(uuid.uuid4())
            
            # Create configs
            download_config = DownloadConfig(
                quality=request.quality or "best",
                format=request.format or "mp4",
                output_directory=request.output_directory or "./downloads",
                audio_format=request.audio_format or "mp3"
            )
            
            batch_config = BatchConfig(
                max_concurrent_downloads=request.max_concurrent_downloads or 3,
                retry_failed_downloads=request.retry_failed_downloads or True
            )
            
            # Create downloader and batch manager
            downloader = VideoDownloader(download_config)
            batch_manager = BatchDownloadManager(downloader, batch_config)
            
            # Convert URLs to video objects (simplified)
            videos = []
            for i, url in enumerate(request.urls):
                video = VideoSearchResult(
                    video_id=f"video_{i}",
                    title=f"Video from {url}",
                    duration=0,
                    uploader="Unknown",
                    upload_date="Unknown",
                    view_count=0,
                    thumbnail_url=""
                )
                videos.append(video)
            
            # Add to queue and start
            batch_manager.add_to_queue(videos)
            self.active_batches[task_id] = batch_manager
            batch_manager.start_batch_download()
            
            return BatchDownloadResponse(
                status=StatusEnum.SUCCESS,
                message=f"Batch download started with {len(videos)} videos",
                task_id=task_id,
                total_videos=len(videos)
            )
            
        except Exception as e:
            self.logger.error(f"Error starting batch download: {e}")
            return BatchDownloadResponse(
                status=StatusEnum.ERROR,
                message=f"Failed to start batch download: {str(e)}",
                task_id="",
                total_videos=0
            )
    
    def get_batch_progress(self, task_id: str) -> BatchProgressResponse:
        """Get progress for a batch download."""
        try:
            if task_id not in self.active_batches:
                return BatchProgressResponse(
                    status=StatusEnum.ERROR,
                    message="Batch download not found",
                    task_id=task_id,
                    overall_progress=0.0,
                    total_videos=0,
                    completed_videos=0,
                    failed_videos=0,
                    active_downloads=0
                )
            
            batch_manager = self.active_batches[task_id]
            progress = batch_manager.get_progress()
            
            return BatchProgressResponse(
                status=StatusEnum.IN_PROGRESS,
                message=f"Batch progress: {progress.overall_progress:.1f}%",
                task_id=task_id,
                overall_progress=progress.overall_progress,
                total_videos=progress.total_videos,
                completed_videos=progress.completed_videos,
                failed_videos=progress.failed_videos,
                active_downloads=progress.active_downloads
            )
            
        except Exception as e:
            self.logger.error(f"Error getting batch progress: {e}")
            return BatchProgressResponse(
                status=StatusEnum.ERROR,
                message=f"Failed to get batch progress: {str(e)}",
                task_id=task_id,
                overall_progress=0.0,
                total_videos=0,
                completed_videos=0,
                failed_videos=0,
                active_downloads=0
            ) 