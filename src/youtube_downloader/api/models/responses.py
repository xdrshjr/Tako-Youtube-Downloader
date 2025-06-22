"""
Pydantic models for API response payloads.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class StatusEnum(str, Enum):
    """Status enumeration for responses."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BaseResponse(BaseModel):
    """Base response model."""
    status: StatusEnum
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VideoInfoResponse(BaseResponse):
    """Response model for video information."""
    video_info: Optional[Dict[str, Any]] = None


class VideoDownloadResponse(BaseResponse):
    """Response model for video download."""
    task_id: Optional[str] = None
    download_url: Optional[str] = None
    output_path: Optional[str] = None
    file_size: Optional[int] = None


class SearchResultItem(BaseModel):
    """Individual search result item."""
    video_id: str
    title: str
    duration: int
    uploader: str
    upload_date: str
    view_count: int
    like_count: Optional[int] = None
    thumbnail_url: str
    url: str
    description: Optional[str] = None


class SearchResponse(BaseResponse):
    """Response model for search results."""
    results: List[SearchResultItem] = []
    total_found: int = 0
    query: str = ""


class BatchTaskInfo(BaseModel):
    """Batch download task information."""
    video_id: str
    title: str
    status: str
    progress: float = 0.0
    error_message: Optional[str] = None
    output_path: Optional[str] = None


class BatchDownloadResponse(BaseResponse):
    """Response model for batch download."""
    task_id: str
    total_videos: int
    tasks: List[BatchTaskInfo] = []


class BatchProgressResponse(BaseResponse):
    """Response model for batch download progress."""
    task_id: str
    overall_progress: float
    total_videos: int
    completed_videos: int
    failed_videos: int
    active_downloads: int
    current_video: Optional[str] = None
    download_speed: Optional[str] = None
    eta: Optional[str] = None
    tasks: List[BatchTaskInfo] = []


class SearchAndDownloadResponse(BaseResponse):
    """Response model for search and download."""
    search_results: SearchResponse
    batch_download: BatchDownloadResponse


class ConfigResponse(BaseResponse):
    """Response model for configuration."""
    config: Dict[str, Any] = {}


class ErrorResponse(BaseResponse):
    """Response model for errors."""
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    status: StatusEnum = StatusEnum.ERROR


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow) 