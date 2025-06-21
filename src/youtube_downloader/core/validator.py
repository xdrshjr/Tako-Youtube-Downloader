"""
URL Validator module for YouTube Downloader.

This module provides functionality to validate YouTube URLs, extract video IDs,
and normalize URLs to standard format.
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Optional


class URLValidator:
    """
    Validates and processes YouTube URLs.
    
    Supports various YouTube URL formats including:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    """
    
    # YouTube URL patterns
    YOUTUBE_DOMAINS = [
        'youtube.com',
        'www.youtube.com',
        'm.youtube.com',
        'youtu.be'
    ]
    
    # Regular expression for video ID extraction
    VIDEO_ID_PATTERN = re.compile(r'[a-zA-Z0-9_-]{11}')
    
    def __init__(self):
        """Initialize the URL validator."""
        pass
    
    def validate_youtube_url(self, url: Optional[str]) -> bool:
        """
        Validate if the given URL is a valid YouTube video URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            bool: True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            parsed_url = urlparse(url)
            
            # Check if domain is YouTube
            if not self._is_youtube_domain(parsed_url.netloc):
                return False
            
            # Check URL format and extract video ID
            video_id = self._extract_video_id_from_parsed_url(parsed_url)
            
            return video_id is not None and self._is_valid_video_id(video_id)
        
        except Exception:
            return False
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            str: Video ID
            
        Raises:
            ValueError: If URL is invalid or video ID cannot be extracted
        """
        if not self.validate_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        try:
            parsed_url = urlparse(url)
            video_id = self._extract_video_id_from_parsed_url(parsed_url)
            
            if not video_id:
                raise ValueError(f"Could not extract video ID from URL: {url}")
            
            return video_id
        
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error extracting video ID from URL: {url}")
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize YouTube URL to standard format.
        
        Args:
            url: YouTube URL in any supported format
            
        Returns:
            str: Normalized URL in format https://www.youtube.com/watch?v=VIDEO_ID
            
        Raises:
            ValueError: If URL is invalid
        """
        video_id = self.extract_video_id(url)
        return f"https://www.youtube.com/watch?v={video_id}"
    
    def _is_youtube_domain(self, netloc: str) -> bool:
        """
        Check if netloc is a YouTube domain.
        
        Args:
            netloc: Network location from parsed URL
            
        Returns:
            bool: True if YouTube domain
        """
        return netloc.lower() in self.YOUTUBE_DOMAINS
    
    def _extract_video_id_from_parsed_url(self, parsed_url) -> Optional[str]:
        """
        Extract video ID from parsed URL object.
        
        Args:
            parsed_url: Parsed URL object
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        netloc = parsed_url.netloc.lower()
        path = parsed_url.path
        query = parsed_url.query
        
        # Handle youtu.be format
        if netloc == 'youtu.be':
            video_id = path.lstrip('/')
            return video_id if self._is_valid_video_id(video_id) else None
        
        # Handle youtube.com formats
        if netloc in ['youtube.com', 'www.youtube.com', 'm.youtube.com']:
            # Check for /watch path with v parameter
            if path == '/watch' or path.startswith('/watch/'):
                query_params = parse_qs(query)
                if 'v' in query_params and query_params['v']:
                    video_id = query_params['v'][0]
                    return video_id if self._is_valid_video_id(video_id) else None
            
            # Check for /embed/ path
            if path.startswith('/embed/'):
                video_id = path.split('/embed/')[-1].split('?')[0]
                return video_id if self._is_valid_video_id(video_id) else None
            
            # Check for /shorts/ path (YouTube Shorts)
            if path.startswith('/shorts/'):
                video_id = path.split('/shorts/')[-1].split('?')[0]
                return video_id if self._is_valid_video_id(video_id) else None
        
        return None
    
    def _is_valid_video_id(self, video_id: str) -> bool:
        """
        Validate if string is a valid YouTube video ID.
        
        Args:
            video_id: String to validate
            
        Returns:
            bool: True if valid video ID format
        """
        if not video_id or len(video_id) != 11:
            return False
        
        return bool(self.VIDEO_ID_PATTERN.fullmatch(video_id))