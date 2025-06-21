"""
Video Downloader module for YouTube Downloader.

This module provides the core video downloading functionality using yt-dlp,
with configuration management and progress tracking.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
import yt_dlp

from .config import DownloadConfig


@dataclass
class VideoInfo:
    """
    Video information data class.
    
    Contains metadata about a YouTube video.
    """
    video_id: str
    title: str
    duration: int
    description: str
    uploader: str
    upload_date: str
    view_count: int
    like_count: Optional[int] = None
    formats: Optional[list] = None


@dataclass
class DownloadResult:
    """
    Download result data class.
    
    Contains the result of a video download operation.
    """
    success: bool
    video_info: Optional[VideoInfo] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None


class VideoDownloader:
    """
    Core video downloader class.
    
    Handles downloading YouTube videos using yt-dlp with configurable options.
    """
    
    def __init__(self, config: DownloadConfig):
        """
        Initialize the video downloader.
        
        Args:
            config: Download configuration
        """
        self.config = config
        self.is_cancelled = False
        self._progress_callback: Optional[Callable] = None
        self._logger = logging.getLogger(__name__)
    
    def download_video(self, url: str) -> DownloadResult:
        """
        Download a video from the given URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            DownloadResult: Result of the download operation
        """
        try:
            # Reset cancellation state
            self.is_cancelled = False
            
            # Create output directory if it doesn't exist
            os.makedirs(self.config.output_directory, exist_ok=True)
            
            # Configure yt-dlp options
            ydl_opts = self._build_yt_dlp_options()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First, get video information
                video_info = self._extract_video_info(ydl, url)
                
                # Check if download was cancelled
                if self.is_cancelled:
                    return DownloadResult(success=False, error_message="Download cancelled")
                
                # Download the video
                ydl.download([url])
                
                # Build output path
                output_path = self._build_output_path(video_info)
                
                # Get file size if file exists
                file_size = None
                if output_path and Path(output_path).exists():
                    file_size = Path(output_path).stat().st_size
                
                return DownloadResult(
                    success=True,
                    video_info=video_info,
                    output_path=output_path,
                    file_size=file_size
                )
        
        except Exception as e:
            self._logger.error(f"Download failed for URL {url}: {str(e)}")
            return DownloadResult(
                success=False,
                error_message=str(e)
            )
    
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Get video information without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoInfo: Video metadata
            
        Raises:
            Exception: If video information cannot be retrieved
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return self._extract_video_info(ydl, url, download=False)
    
    def cancel_download(self) -> None:
        """Cancel the current download operation."""
        self.is_cancelled = True
        self._logger.info("Download cancellation requested")
    
    def reset_cancellation(self) -> None:
        """Reset the cancellation state."""
        self.is_cancelled = False
    
    def set_progress_callback(self, callback: Callable) -> None:
        """
        Set progress callback function.
        
        Args:
            callback: Function to call with progress updates
        """
        self._progress_callback = callback
    
    def _build_yt_dlp_options(self) -> Dict[str, Any]:
        """
        Build yt-dlp options from configuration.
        
        Returns:
            Dict[str, Any]: yt-dlp options dictionary
        """
        # Build format selector based on quality setting
        format_selector = self._build_format_selector()
        
        # Build output template - convert our format to yt-dlp format
        output_template = self._convert_naming_pattern_to_ytdlp_format()
        
        options = {
            'format': format_selector,
            'outtmpl': output_template,
            'extract_flat': False,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'no_warnings': False,
            'retries': self.config.retry_attempts,
            'socket_timeout': self.config.timeout,
        }
        
        # Add progress hook if callback is set
        if self._progress_callback:
            options['progress_hooks'] = [self._progress_hook]
        
        # Add rate limiting if configured
        if self.config.rate_limit:
            options['ratelimit'] = self.config.rate_limit
        
        return options
    
    def _convert_naming_pattern_to_ytdlp_format(self) -> str:
        """
        Convert our naming pattern to yt-dlp format.
        
        Our format: {title}-{id}.{ext}
        yt-dlp format: %(title)s-%(id)s.%(ext)s
        
        Returns:
            str: Output template for yt-dlp
        """
        # Convert our {field} format to yt-dlp %(field)s format
        ytdlp_pattern = self.config.naming_pattern
        ytdlp_pattern = ytdlp_pattern.replace('{title}', '%(title)s')
        ytdlp_pattern = ytdlp_pattern.replace('{id}', '%(id)s')
        ytdlp_pattern = ytdlp_pattern.replace('{ext}', '%(ext)s')
        ytdlp_pattern = ytdlp_pattern.replace('{uploader}', '%(uploader)s')
        ytdlp_pattern = ytdlp_pattern.replace('{upload_date}', '%(upload_date)s')
        
        return os.path.join(self.config.output_directory, ytdlp_pattern)
    
    def _build_format_selector(self) -> str:
        """
        Build format selector string for yt-dlp.
        
        Returns:
            str: Format selector string
        """
        if self.config.quality == "best":
            return "best"
        elif self.config.quality == "worst":
            return "worst"
        else:
            # Parse quality (e.g., "720p" -> 720)
            try:
                height = int(self.config.quality.replace('p', ''))
                return f"best[height<={height}]"
            except ValueError:
                return "best"
    
    def _extract_video_info(self, ydl, url: str, download: bool = True) -> VideoInfo:
        """
        Extract video information using yt-dlp.
        
        Args:
            ydl: YoutubeDL instance
            url: Video URL
            download: Whether this is for download (affects info extraction)
            
        Returns:
            VideoInfo: Extracted video information
        """
        info = ydl.extract_info(url, download=download)
        
        return VideoInfo(
            video_id=info.get('id', ''),
            title=info.get('title', ''),
            duration=info.get('duration', 0),
            description=info.get('description', ''),
            uploader=info.get('uploader', ''),
            upload_date=info.get('upload_date', ''),
            view_count=info.get('view_count', 0),
            like_count=info.get('like_count'),
            formats=info.get('formats', [])
        )
    
    def _build_output_path(self, video_info: VideoInfo) -> str:
        """
        Build the expected output file path.
        
        Args:
            video_info: Video information
            
        Returns:
            str: Expected output file path
        """
        # Replace placeholders in naming pattern
        filename = self.config.naming_pattern.format(
            title=self._sanitize_filename(video_info.title),
            id=video_info.video_id,
            ext=self.config.format
        )
        
        return os.path.join(self.config.output_directory, filename)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to remove invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit filename length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename.strip()
    
    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Progress hook for yt-dlp.
        
        Args:
            d: Progress data from yt-dlp
        """
        if self._progress_callback:
            self._progress_callback(d)
        
        # Check for cancellation
        if self.is_cancelled:
            raise KeyboardInterrupt("Download cancelled by user")