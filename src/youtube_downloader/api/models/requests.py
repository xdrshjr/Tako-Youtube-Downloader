"""
Pydantic models for API request payloads.
"""

from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field, field_validator


class VideoDownloadRequest(BaseModel):
    """Request model for video download."""
    url: str = Field(..., description="YouTube video URL")
    quality: Optional[str] = Field("best", description="Video quality (best, worst, 720p, 1080p, 480p, 360p)")
    format: Optional[str] = Field("mp4", description="Output format (mp4, webm, mkv)")
    output_directory: Optional[str] = Field("./downloads", description="Output directory path")
    audio_format: Optional[str] = Field("mp3", description="Audio format (mp3, aac, opus)")


class VideoInfoRequest(BaseModel):
    """Request model for video information."""
    url: str = Field(..., description="YouTube video URL")


class SearchRequest(BaseModel):
    """Request model for video search."""
    query: str = Field(..., description="Search query")
    max_results: Optional[int] = Field(10, description="Maximum number of results", ge=1, le=100)
    sort_by: Optional[str] = Field("relevance", description="Sort by (relevance, upload_date, view_count, rating)")
    upload_date: Optional[str] = Field("any", description="Upload date filter (hour, today, week, month, year, any)")
    min_duration: Optional[int] = Field(None, description="Minimum duration in seconds", ge=0)
    max_duration: Optional[int] = Field(None, description="Maximum duration in seconds", ge=0)
    min_view_count: Optional[int] = Field(None, description="Minimum view count", ge=0)
    exclude_shorts: Optional[bool] = Field(True, description="Exclude YouTube Shorts")
    exclude_live: Optional[bool] = Field(True, description="Exclude live streams")


class BatchDownloadRequest(BaseModel):
    """Request model for batch download."""
    urls: List[str] = Field(..., description="List of YouTube video URLs")
    quality: Optional[str] = Field("best", description="Video quality")
    format: Optional[str] = Field("mp4", description="Output format")
    output_directory: Optional[str] = Field("./downloads", description="Output directory path")
    audio_format: Optional[str] = Field("mp3", description="Audio format")
    max_concurrent_downloads: Optional[int] = Field(3, description="Maximum concurrent downloads", ge=1, le=10)
    retry_failed_downloads: Optional[bool] = Field(True, description="Retry failed downloads")
    
    @field_validator('urls')
    @classmethod
    def validate_urls_not_empty(cls, v):
        if not v:
            raise ValueError('URLs list cannot be empty')
        return v


class SearchAndDownloadRequest(BaseModel):
    """Request model for search and batch download."""
    search: SearchRequest
    download: VideoDownloadRequest


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration update."""
    quality: Optional[str] = Field(None, description="Default video quality")
    format: Optional[str] = Field(None, description="Default output format")
    output_directory: Optional[str] = Field(None, description="Default output directory")
    audio_format: Optional[str] = Field(None, description="Default audio format")
    max_concurrent_downloads: Optional[int] = Field(None, description="Default max concurrent downloads", ge=1, le=10) 