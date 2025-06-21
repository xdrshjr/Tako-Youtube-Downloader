"""
Video filtering module for YouTube Downloader.

This module provides video filtering functionality for search results based on
various criteria such as duration, view count, upload date, and content type.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import logging

from .search_config import FilterConfig


@dataclass
class VideoSearchResult:
    """
    Data class representing a YouTube video search result.
    
    Contains essential metadata about a video returned from search results.
    """
    video_id: str
    title: str
    duration: int  # Duration in seconds
    uploader: str
    upload_date: str  # ISO format date string (YYYY-MM-DD)
    view_count: int
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    like_count: Optional[int] = None
    
    def get_url(self) -> str:
        """
        Generate YouTube URL from video ID.
        
        Returns:
            str: Complete YouTube URL for this video
        """
        return f"https://www.youtube.com/watch?v={self.video_id}"
    
    def is_short(self) -> bool:
        """
        Check if this video is a YouTube Short.
        
        Returns:
            bool: True if video is under 60 seconds (YouTube Short)
        """
        # Live streams have duration=0 but are not YouTube Shorts
        if self.is_live_stream():
            return False
        return self.duration < 60
    
    def is_live_stream(self) -> bool:
        """
        Check if this video is a live stream.
        
        Returns:
            bool: True if video has 0 duration (indicating live stream)
        """
        return self.duration == 0
    
    def get_duration_formatted(self) -> str:
        """
        Get human-readable duration format.
        
        Returns:
            str: Duration in MM:SS or HH:MM:SS format
        """
        if self.duration == 0:
            return "LIVE"
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class VideoFilter:
    """
    Video filtering class for processing YouTube search results.
    
    Provides comprehensive filtering functionality based on duration, view count,
    upload date, content type, and other criteria.
    """
    
    def __init__(self, filter_config: FilterConfig):
        """
        Initialize the video filter.
        
        Args:
            filter_config: Configuration object containing filtering parameters
        """
        self.filter_config = filter_config
        self._logger = logging.getLogger(__name__)
        
        self._logger.info("VideoFilter initialized", extra={
            'min_duration': filter_config.min_duration,
            'max_duration': filter_config.max_duration,
            'exclude_shorts': filter_config.exclude_shorts,
            'exclude_live': filter_config.exclude_live
        })
    
    def filter_by_duration(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]:
        """
        Filter videos by duration range.
        
        Args:
            videos: List of video search results to filter
            
        Returns:
            List[VideoSearchResult]: Filtered video list
        """
        if not videos:
            return []
        
        filtered = []
        min_duration = self.filter_config.min_duration
        max_duration = self.filter_config.max_duration
        
        for video in videos:
            # Skip duration filtering for live streams unless specifically configured
            if video.is_live_stream() and not self.filter_config.exclude_live:
                filtered.append(video)
                continue
            
            # Apply duration filters
            if min_duration is not None and video.duration < min_duration:
                continue
            
            if max_duration is not None and video.duration > max_duration:
                continue
            
            filtered.append(video)
        
        self._logger.debug(f"Duration filter: {len(videos)} -> {len(filtered)} videos")
        return filtered
    
    def filter_by_view_count(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]:
        """
        Filter videos by minimum view count.
        
        Args:
            videos: List of video search results to filter
            
        Returns:
            List[VideoSearchResult]: Filtered video list
        """
        if not videos or self.filter_config.min_view_count is None:
            return videos
        
        min_views = self.filter_config.min_view_count
        filtered = [video for video in videos if video.view_count >= min_views]
        
        self._logger.debug(f"View count filter: {len(videos)} -> {len(filtered)} videos")
        return filtered
    
    def filter_by_upload_date(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]:
        """
        Filter videos by upload date.
        
        Args:
            videos: List of video search results to filter
            
        Returns:
            List[VideoSearchResult]: Filtered video list
        """
        if not videos or self.filter_config.min_upload_date is None:
            return videos
        
        try:
            # Parse the minimum upload date
            min_date = datetime.fromisoformat(self.filter_config.min_upload_date)
        except ValueError:
            self._logger.warning(
                f"Invalid min_upload_date format: {self.filter_config.min_upload_date}. "
                "Expected ISO format (YYYY-MM-DD). Skipping date filter."
            )
            return videos
        
        filtered = []
        for video in videos:
            try:
                video_date = datetime.fromisoformat(video.upload_date)
                if video_date >= min_date:
                    filtered.append(video)
            except ValueError:
                # If video date is invalid, include the video and log warning
                self._logger.warning(
                    f"Invalid upload_date format for video {video.video_id}: {video.upload_date}"
                )
                filtered.append(video)
        
        self._logger.debug(f"Upload date filter: {len(videos)} -> {len(filtered)} videos")
        return filtered
    
    def exclude_shorts_filter(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]:
        """
        Filter out YouTube Shorts (videos under 60 seconds).
        
        Args:
            videos: List of video search results to filter
            
        Returns:
            List[VideoSearchResult]: Filtered video list without shorts
        """
        if not videos or not self.filter_config.exclude_shorts:
            return videos
        
        filtered = [video for video in videos if not video.is_short()]
        
        self._logger.debug(f"Shorts exclusion: {len(videos)} -> {len(filtered)} videos")
        return filtered
    
    def exclude_live_filter(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]:
        """
        Filter out live streams.
        
        Args:
            videos: List of video search results to filter
            
        Returns:
            List[VideoSearchResult]: Filtered video list without live streams
        """
        if not videos or not self.filter_config.exclude_live:
            return videos
        
        filtered = [video for video in videos if not video.is_live_stream()]
        
        self._logger.debug(f"Live stream exclusion: {len(videos)} -> {len(filtered)} videos")
        return filtered
    
    def filter_by_quality(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]:
        """
        Filter videos by minimum quality requirement.
        
        Note: This is a placeholder implementation as quality information
        is not available in search results. Quality filtering would need
        to be implemented during the download phase.
        
        Args:
            videos: List of video search results to filter
            
        Returns:
            List[VideoSearchResult]: Filtered video list
        """
        if not videos or self.filter_config.min_quality is None:
            return videos
        
        # Quality filtering would require additional API calls to get format info
        # For now, we'll log this requirement and return all videos
        self._logger.info(
            f"Quality filtering requested ({self.filter_config.min_quality}) "
            "but will be applied during download phase"
        )
        
        return videos
    
    def apply_all_filters(self, videos: List[VideoSearchResult]) -> List[VideoSearchResult]:
        """
        Apply all configured filters in sequence.
        
        Args:
            videos: List of video search results to filter
            
        Returns:
            List[VideoSearchResult]: Filtered video list after applying all filters
        """
        if not videos:
            return []
        
        self._logger.info(f"Starting filtering with {len(videos)} videos")
        
        # Apply filters in logical order
        filtered = videos
        
        # 1. Content type filters (shorts, live streams)
        filtered = self.exclude_shorts_filter(filtered)
        filtered = self.exclude_live_filter(filtered)
        
        # 2. Duration filters
        filtered = self.filter_by_duration(filtered)
        
        # 3. View count filter
        filtered = self.filter_by_view_count(filtered)
        
        # 4. Upload date filter
        filtered = self.filter_by_upload_date(filtered)
        
        # 5. Quality filter (placeholder)
        filtered = self.filter_by_quality(filtered)
        
        self._logger.info(
            f"Filtering complete: {len(videos)} -> {len(filtered)} videos",
            extra={
                'original_count': len(videos),
                'filtered_count': len(filtered),
                'filter_efficiency': f"{(len(filtered) / len(videos) * 100):.1f}%" if videos else "0%"
            }
        )
        
        return filtered
    
    def get_filter_summary(self) -> dict:
        """
        Get a summary of current filter configuration.
        
        Returns:
            dict: Summary of active filters
        """
        summary = {
            'duration_range': None,
            'min_view_count': self.filter_config.min_view_count,
            'min_upload_date': self.filter_config.min_upload_date,
            'exclude_shorts': self.filter_config.exclude_shorts,
            'exclude_live': self.filter_config.exclude_live,
            'min_quality': self.filter_config.min_quality
        }
        
        # Format duration range
        if self.filter_config.min_duration or self.filter_config.max_duration:
            min_dur = self.filter_config.min_duration or 0
            max_dur = self.filter_config.max_duration or "∞"
            summary['duration_range'] = f"{min_dur}s - {max_dur}s"
        
        return summary
    
    def count_filtered_by_criteria(self, videos: List[VideoSearchResult]) -> dict:
        """
        Count how many videos would be filtered by each criteria.
        
        Args:
            videos: List of video search results to analyze
            
        Returns:
            dict: Count of videos filtered by each criteria
        """
        if not videos:
            return {}
        
        counts = {
            'total': len(videos),
            'shorts': 0,
            'live_streams': 0,
            'duration_too_short': 0,
            'duration_too_long': 0,
            'view_count_too_low': 0,
            'upload_date_too_old': 0
        }
        
        for video in videos:
            if video.is_short():
                counts['shorts'] += 1
            
            if video.is_live_stream():
                counts['live_streams'] += 1
            
            if (self.filter_config.min_duration and 
                video.duration < self.filter_config.min_duration):
                counts['duration_too_short'] += 1
            
            if (self.filter_config.max_duration and 
                video.duration > self.filter_config.max_duration):
                counts['duration_too_long'] += 1
            
            if (self.filter_config.min_view_count and 
                video.view_count < self.filter_config.min_view_count):
                counts['view_count_too_low'] += 1
            
            # Upload date filtering (with error handling)
            if self.filter_config.min_upload_date:
                try:
                    min_date = datetime.fromisoformat(self.filter_config.min_upload_date)
                    video_date = datetime.fromisoformat(video.upload_date)
                    if video_date < min_date:
                        counts['upload_date_too_old'] += 1
                except ValueError:
                    pass  # Skip if date parsing fails
        
        return counts 