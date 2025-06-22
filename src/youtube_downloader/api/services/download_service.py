"""
Download service for handling video download operations.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from pathlib import Path

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
    StatusEnum,
    ErrorResponse
)


class DownloadService:
    """Service for handling video download operations."""
    
    def __init__(self):
        """Initialize the download service."""
        self.logger = logging.getLogger(__name__)
        self.validator = URLValidator()
        self.config_manager = ConfigManager()
        self.active_downloads: Dict[str, VideoDownloader] = {}
    
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
            
            # Start download
            result = downloader.download_video(request.url)
            
            # Clean up
            if task_id in self.active_downloads:
                del self.active_downloads[task_id]
            
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