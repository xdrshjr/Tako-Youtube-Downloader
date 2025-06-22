"""
Download service for handling video download operations.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ...core import (
    URLValidator,
    VideoDownloader,
    DownloadConfig,
    ConfigManager,
    DownloadResult,
    VideoInfo
)
from ..models.requests import VideoDownloadRequest, VideoInfoRequest
from ..models.responses import (
    VideoDownloadResponse,
    VideoInfoResponse,
    DownloadStatusResponse,
    StatusEnum,
    ErrorResponse
)


class DownloadTaskInfo:
    """Information about a download task."""
    
    def __init__(self, task_id: str, url: str, title: str = None):
        self.task_id = task_id
        self.url = url
        self.title = title
        self.status = StatusEnum.PENDING
        self.progress = 0.0
        self.output_path = None
        self.file_size = None
        self.error_message = None
        self.started_at = datetime.utcnow()
        self.completed_at = None


class DownloadService:
    """Service for handling video download operations."""
    
    def __init__(self):
        """Initialize the download service."""
        self.logger = logging.getLogger(__name__)
        self.validator = URLValidator()
        self.config_manager = ConfigManager()
        self.active_downloads: Dict[str, VideoDownloader] = {}
        self.download_tasks: Dict[str, DownloadTaskInfo] = {}
        
        # Task cleanup settings - keep completed tasks for 24 hours
        self.task_retention_hours = 24
    
    def get_video_info(self, request: VideoInfoRequest) -> VideoInfoResponse:
        """
        Get video information without downloading.
        
        Args:
            request: Video info request
            
        Returns:
            Video information response
        """
        try:
            # Validate URL
            if not self.validator.validate_youtube_url(request.url):
                return VideoInfoResponse(
                    status=StatusEnum.ERROR,
                    message="Invalid YouTube URL"
                )
            
            # Get default config
            config = self.config_manager.get_config()
            downloader = VideoDownloader(config)
            
            # Get video info
            video_info = downloader.get_video_info(request.url)
            
            # Convert to dict for response
            video_info_dict = {
                "video_id": self.validator.extract_video_id(request.url),
                "title": video_info.title,
                "uploader": video_info.uploader,
                "duration": video_info.duration,
                "upload_date": video_info.upload_date,
                "view_count": video_info.view_count,
                "like_count": video_info.like_count,
                "description": video_info.description[:500] if video_info.description else None,  # Truncate description
                "thumbnail_url": video_info.thumbnail_url,
                "url": request.url
            }
            
            return VideoInfoResponse(
                status=StatusEnum.SUCCESS,
                message="Video information retrieved successfully",
                video_info=video_info_dict
            )
            
        except Exception as e:
            self.logger.error(f"Error getting video info: {e}")
            return VideoInfoResponse(
                status=StatusEnum.ERROR,
                message=f"Failed to get video information: {str(e)}"
            )
    
    def download_video(self, request: VideoDownloadRequest) -> VideoDownloadResponse:
        """
        Download a single video.
        
        Args:
            request: Video download request
            
        Returns:
            Video download response
        """
        try:
            # Validate URL
            if not self.validator.validate_youtube_url(request.url):
                return VideoDownloadResponse(
                    status=StatusEnum.ERROR,
                    message="Invalid YouTube URL"
                )
            
            # Create task ID
            task_id = str(uuid.uuid4())
            
            # Get video info first to get title
            try:
                config = self.config_manager.get_config()
                temp_downloader = VideoDownloader(config)
                video_info = temp_downloader.get_video_info(request.url)
                video_title = video_info.title
            except Exception as e:
                self.logger.warning(f"Could not get video title: {e}")
                video_title = "Unknown"
            
            # Create task info
            task_info = DownloadTaskInfo(task_id, request.url, video_title)
            self.download_tasks[task_id] = task_info
            
            # Create download config from request
            config = DownloadConfig(
                quality=request.quality or "best",
                format=request.format or "mp4",
                output_directory=request.output_directory or "./downloads",
                audio_format=request.audio_format or "mp3"
            )
            
            # Ensure output directory exists
            Path(config.output_directory).mkdir(parents=True, exist_ok=True)
            
            # Create downloader
            downloader = VideoDownloader(config)
            self.active_downloads[task_id] = downloader
            
            # Update status to in progress
            task_info.status = StatusEnum.IN_PROGRESS
            task_info.progress = 0.0
            
            # Start download
            result = downloader.download_video(request.url)
            
            # Update task info based on result
            task_info.completed_at = datetime.utcnow()
            if result.success:
                task_info.status = StatusEnum.COMPLETED
                task_info.progress = 100.0
                task_info.output_path = result.output_path
                task_info.file_size = result.file_size
            else:
                task_info.status = StatusEnum.ERROR
                task_info.error_message = result.error_message
            
            # Clean up active downloads but keep task info for file access
            if task_id in self.active_downloads:
                del self.active_downloads[task_id]
            
            # Log completion for reference
            self.logger.info(f"Download completed | task_id={task_id} video_id={self.validator.extract_video_id(request.url) if hasattr(self.validator, 'extract_video_id') else 'unknown'} file_size={result.file_size/1024/1024:.1f} MB duration={(datetime.utcnow() - task_info.started_at).total_seconds():.1f}s action=download_complete")
            
            if result.success:
                return VideoDownloadResponse(
                    status=StatusEnum.SUCCESS,
                    message="Video downloaded successfully",
                    task_id=task_id,
                    download_url=request.url,
                    output_path=result.output_path,
                    file_size=result.file_size
                )
            else:
                return VideoDownloadResponse(
                    status=StatusEnum.ERROR,
                    message=f"Download failed: {result.error_message}",
                    task_id=task_id,
                    download_url=request.url
                )
                
        except Exception as e:
            self.logger.error(f"Error downloading video: {e}")
            
            # Update task status if it exists
            if 'task_id' in locals() and task_id in self.download_tasks:
                task_info = self.download_tasks[task_id]
                task_info.status = StatusEnum.ERROR
                task_info.error_message = str(e)
                task_info.completed_at = datetime.utcnow()
            
            return VideoDownloadResponse(
                status=StatusEnum.ERROR,
                message=f"Download failed: {str(e)}"
            )
    
    def cancel_download(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel an active download.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            Cancellation result
        """
        try:
            if task_id in self.active_downloads:
                downloader = self.active_downloads[task_id]
                downloader.cancel_download()
                del self.active_downloads[task_id]
                return {
                    "status": "success",
                    "message": f"Download {task_id} cancelled successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Download {task_id} not found or already completed"
                }
        except Exception as e:
            self.logger.error(f"Error cancelling download: {e}")
            return {
                "status": "error",
                "message": f"Failed to cancel download: {str(e)}"
            }
    
    def get_active_downloads(self) -> Dict[str, Any]:
        """
        Get list of active downloads.
        
        Returns:
            Active downloads information
        """
        return {
            "active_downloads": list(self.active_downloads.keys()),
            "count": len(self.active_downloads)
        }
    
    def _cleanup_old_tasks(self):
        """Clean up old completed tasks to free memory."""
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=self.task_retention_hours)
            
            tasks_to_remove = []
            for task_id, task_info in self.download_tasks.items():
                # Only clean up completed or failed tasks that are old enough
                if (task_info.status in [StatusEnum.COMPLETED, StatusEnum.ERROR] and 
                    task_info.completed_at and 
                    task_info.completed_at < cutoff_time):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.download_tasks[task_id]
                
            if tasks_to_remove:
                self.logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
                
        except Exception as e:
            self.logger.error(f"Error during task cleanup: {e}")

    def get_download_status(self, task_id: str) -> DownloadStatusResponse:
        """
        Get the status of a download task.
        
        Args:
            task_id: Task ID to check status for
            
        Returns:
            Download status response
        """
        try:
            # Clean up old tasks periodically
            self._cleanup_old_tasks()
            
            if task_id not in self.download_tasks:
                return DownloadStatusResponse(
                    status=StatusEnum.ERROR,
                    message=f"Download task {task_id} not found or expired",
                    task_id=task_id,
                    download_status=StatusEnum.ERROR
                )
            
            task_info = self.download_tasks[task_id]
            
            return DownloadStatusResponse(
                status=StatusEnum.SUCCESS,
                message="Download status retrieved successfully",
                task_id=task_id,
                download_status=task_info.status,
                download_url=task_info.url,
                output_path=task_info.output_path,
                file_size=task_info.file_size,
                progress=task_info.progress,
                error_message=task_info.error_message,
                video_title=task_info.title,
                started_at=task_info.started_at,
                completed_at=task_info.completed_at
            )
            
        except Exception as e:
            self.logger.error(f"Error getting download status: {e}")
            return DownloadStatusResponse(
                status=StatusEnum.ERROR,
                message=f"Failed to get download status: {str(e)}",
                task_id=task_id,
                download_status=StatusEnum.ERROR
            ) 