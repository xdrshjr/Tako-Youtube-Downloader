"""
Search engine module for YouTube Downloader.

This module provides YouTube video search functionality using yt-dlp,
with comprehensive error handling and result processing.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import yt_dlp

from .search_config import SearchConfig
from .video_filter import VideoSearchResult, VideoFilter


class SearchError(Exception):
    """Base exception for search-related errors."""
    pass


class NetworkSearchError(SearchError):
    """Exception for network-related search errors."""
    pass


class YouTubeSearchError(SearchError):
    """Exception for YouTube-specific search errors."""
    pass


class SearchEngine:
    """
    YouTube search engine using yt-dlp.
    
    Provides comprehensive video search functionality with filtering,
    error handling, and result processing capabilities.
    """
    
    def __init__(self, config: SearchConfig):
        """
        Initialize the search engine.
        
        Args:
            config: Search configuration containing query, filters, and options
        """
        self.config = config
        self._logger = logging.getLogger(__name__)
        
        # Initialize video filter
        self.video_filter = VideoFilter(config.filter_config)
        
        self._logger.info("SearchEngine initialized", extra={
            'search_query': config.search_query,
            'max_results': config.max_results,
            'sort_by': config.sort_by
        })
    
    def search_videos(self, query: str, max_results: Optional[int] = None) -> List[VideoSearchResult]:
        """
        Search for YouTube videos using the specified query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (overrides config)
            
        Returns:
            List[VideoSearchResult]: List of filtered video search results
            
        Raises:
            NetworkSearchError: For network-related errors
            YouTubeSearchError: For YouTube-specific errors
            SearchError: For other search-related errors
        """
        if not query.strip():
            self._logger.warning("Empty search query provided")
            return []
        
        # Use provided max_results or fall back to config
        max_results = max_results or self.config.max_results
        
        self._logger.info(f"Starting video search", extra={
            'query': query,
            'max_results': max_results,
            'sort_by': self.config.sort_by
        })
        
        try:
            # Build search URL
            search_url = self._build_search_url(query, max_results)
            
            # Configure yt-dlp options
            yt_dlp_opts = self._build_yt_dlp_options()
            
            # Perform search
            with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
                search_result = ydl.extract_info(search_url, download=False)
            
            # Process search results
            videos = self._process_search_results(search_result)
            
            # Apply filters
            filtered_videos = self.video_filter.apply_all_filters(videos)
            
            self._logger.info(f"Search completed", extra={
                'query': query,
                'raw_results': len(videos),
                'filtered_results': len(filtered_videos)
            })
            
            return filtered_videos
            
        except Exception as e:
            error_type = self._classify_search_error(e)
            self._logger.error(f"Search failed: {str(e)}", extra={
                'query': query,
                'error_type': error_type,
                'error_message': str(e)
            })
            raise error_type(f"Search failed for query '{query}': {str(e)}")
    
    def get_video_details(self, video_ids: List[str]) -> List[VideoSearchResult]:
        """
        Get detailed information for specific video IDs.
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List[VideoSearchResult]: Detailed video information
            
        Note:
            This is a placeholder for future implementation.
        """
        raise NotImplementedError("get_video_details will be implemented in future versions")
    
    def _build_search_url(self, query: str, max_results: int) -> str:
        """
        Build yt-dlp search URL.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            str: yt-dlp compatible search URL
        """
        # Use yt-dlp's ytsearch prefix for YouTube search
        return f"ytsearch{max_results}:{query}"
    
    def _build_yt_dlp_options(self) -> Dict[str, Any]:
        """
        Build yt-dlp options for search.
        
        Returns:
            Dict[str, Any]: yt-dlp configuration options
        """
        options = {
            'quiet': True,
            'no_warnings': False,
            'extract_flat': False,
            'ignoreerrors': True,
            'logtostderr': False,
        }
        
        # Add date filtering if specified
        if self.config.upload_date != "any":
            options['dateafter'] = self._convert_upload_date_filter(self.config.upload_date)
        
        # Add sort order
        if self.config.sort_by == "upload_date":
            options['sort'] = "date"
        elif self.config.sort_by == "view_count":
            options['sort'] = "views"
        elif self.config.sort_by == "rating":
            options['sort'] = "rating"
        # relevance is default, no special option needed
        
        return options
    
    def _convert_upload_date_filter(self, upload_date: str) -> str:
        """
        Convert upload date filter to yt-dlp format.
        
        Args:
            upload_date: Upload date filter ("hour", "today", "week", etc.)
            
        Returns:
            str: yt-dlp compatible date string
        """
        # Map upload_date values to actual dates
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        date_map = {
            "hour": now - timedelta(hours=1),
            "today": now - timedelta(days=1),
            "week": now - timedelta(weeks=1),
            "month": now - timedelta(days=30),
            "year": now - timedelta(days=365),
        }
        
        if upload_date in date_map:
            return date_map[upload_date].strftime("%Y%m%d")
        
        return ""  # Default to no date filter
    
    def _process_search_results(self, search_result: Dict[str, Any]) -> List[VideoSearchResult]:
        """
        Process yt-dlp search results into VideoSearchResult objects.
        
        Args:
            search_result: Raw yt-dlp search result dictionary
            
        Returns:
            List[VideoSearchResult]: Processed video results
        """
        if not search_result or 'entries' not in search_result:
            self._logger.warning("No entries found in search results")
            return []
        
        videos = []
        entries = search_result['entries']
        
        for entry in entries:
            if not entry:  # Skip None entries
                continue
            
            # Validate required metadata
            if not self._validate_video_metadata(entry):
                self._logger.debug(f"Skipping video with incomplete metadata: {entry.get('id', 'unknown')}")
                continue
            
            try:
                video = VideoSearchResult(
                    video_id=entry['id'],
                    title=entry['title'],
                    duration=int(entry.get('duration', 0)),
                    uploader=entry.get('uploader', 'Unknown'),
                    upload_date=self._parse_upload_date(entry.get('upload_date')),
                    view_count=int(entry.get('view_count', 0)),
                    thumbnail_url=entry.get('thumbnail'),
                    description=entry.get('description'),
                    like_count=entry.get('like_count')
                )
                videos.append(video)
                
            except (ValueError, TypeError) as e:
                self._logger.warning(f"Error processing video entry {entry.get('id', 'unknown')}: {e}")
                continue
        
        self._logger.debug(f"Processed {len(videos)} valid videos from {len(entries)} entries")
        return videos
    
    def _validate_video_metadata(self, entry: Dict[str, Any]) -> bool:
        """
        Validate that video entry has required metadata.
        
        Args:
            entry: Video entry dictionary from yt-dlp
            
        Returns:
            bool: True if entry has all required fields
        """
        required_fields = ['id', 'title', 'duration', 'uploader', 'upload_date']
        
        for field in required_fields:
            if field not in entry or entry[field] is None:
                return False
        
        # Additional validation for specific fields
        if not isinstance(entry.get('duration'), (int, float)):
            return False
        
        if not entry.get('title', '').strip():
            return False
        
        return True
    
    def _parse_upload_date(self, upload_date: Any) -> str:
        """
        Parse upload date from yt-dlp format to ISO format.
        
        Args:
            upload_date: Upload date in yt-dlp format (YYYYMMDD)
            
        Returns:
            str: ISO format date string (YYYY-MM-DD)
        """
        if not upload_date:
            return "1970-01-01"  # Default fallback
        
        try:
            # yt-dlp typically returns dates as YYYYMMDD strings
            date_str = str(upload_date)
            if len(date_str) == 8 and date_str.isdigit():
                # Parse YYYYMMDD format
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                return f"{year}-{month}-{day}"
            else:
                # Try to parse as ISO date
                from datetime import datetime
                datetime.fromisoformat(date_str)
                return date_str
        except (ValueError, TypeError, NameError):
            self._logger.warning(f"Invalid upload date format: {upload_date}")
            return "1970-01-01"  # Default fallback
    
    def _classify_search_error(self, error: Exception) -> type:
        """
        Classify search error to appropriate exception type.
        
        Args:
            error: Original exception
            
        Returns:
            type: Appropriate exception class
        """
        error_message = str(error).lower()
        
        # Check exception type first
        if isinstance(error, PermissionError):
            return YouTubeSearchError
        
        # Network-related errors
        if any(keyword in error_message for keyword in 
               ['network', 'connection', 'timeout', 'dns', 'socket']):
            return NetworkSearchError
        
        # YouTube-specific errors
        if any(keyword in error_message for keyword in 
               ['youtube', 'api', 'quota', 'permission', 'blocked', 'unavailable']):
            return YouTubeSearchError
        
        # Default to generic search error
        return SearchError 