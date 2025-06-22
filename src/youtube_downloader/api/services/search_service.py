"""
Search service for handling video search operations.
"""

import logging
from typing import List, Dict, Any

from ...core import (
    SearchEngine,
    SearchConfig,
    FilterConfig,
    VideoSearchResult,
    SearchError,
    NetworkSearchError,
    YouTubeSearchError
)
from ..models.requests import SearchRequest
from ..models.responses import (
    SearchResponse,
    SearchResultItem,
    StatusEnum
)


class SearchService:
    """Service for handling video search operations."""
    
    def __init__(self):
        """Initialize the search service."""
        self.logger = logging.getLogger(__name__)
    
    def search_videos(self, request: SearchRequest) -> SearchResponse:
        """
        Search for videos based on query and filters.
        
        Args:
            request: Search request
            
        Returns:
            Search response with results
        """
        try:
            # Create filter configuration
            filter_config = FilterConfig(
                min_duration=request.min_duration,
                max_duration=request.max_duration,
                min_view_count=request.min_view_count,
                exclude_shorts=request.exclude_shorts or False,
                exclude_live=request.exclude_live or False
            )
            
            # Create search configuration
            search_config = SearchConfig(
                search_query=request.query,
                max_results=request.max_results or 10,
                sort_by=request.sort_by or "relevance",
                upload_date=request.upload_date or "any",
                filter_config=filter_config
            )
            
            # Execute search
            search_engine = SearchEngine(search_config)
            videos = search_engine.search_videos(request.query)
            
            # Convert results to response format
            search_results = []
            for video in videos:
                result_item = SearchResultItem(
                    video_id=video.video_id,
                    title=video.title,
                    duration=video.duration,
                    uploader=video.uploader,
                    upload_date=video.upload_date,
                    view_count=video.view_count,
                    like_count=video.like_count,
                    thumbnail_url=video.thumbnail_url,
                    url=video.get_url(),
                    description=video.description[:200] if video.description else None  # Truncate description
                )
                search_results.append(result_item)
            
            return SearchResponse(
                status=StatusEnum.SUCCESS,
                message=f"Found {len(search_results)} videos",
                results=search_results,
                total_found=len(search_results),
                query=request.query
            )
            
        except NetworkSearchError as e:
            self.logger.error(f"Network error during search: {e}")
            return SearchResponse(
                status=StatusEnum.ERROR,
                message=f"Network error: {str(e)}",
                query=request.query
            )
            
        except YouTubeSearchError as e:
            self.logger.error(f"YouTube search error: {e}")
            return SearchResponse(
                status=StatusEnum.ERROR,
                message=f"YouTube search error: {str(e)}",
                query=request.query
            )
            
        except SearchError as e:
            self.logger.error(f"Search error: {e}")
            return SearchResponse(
                status=StatusEnum.ERROR,
                message=f"Search error: {str(e)}",
                query=request.query
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during search: {e}")
            return SearchResponse(
                status=StatusEnum.ERROR,
                message=f"Unexpected error: {str(e)}",
                query=request.query
            )
    
    def get_trending_videos(self, max_results: int = 10) -> SearchResponse:
        """
        Get trending videos (popular videos).
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            Search response with trending videos
        """
        try:
            # Search for trending content
            request = SearchRequest(
                query="trending",
                max_results=max_results,
                sort_by="view_count",
                min_view_count=100000  # Only popular videos
            )
            
            return self.search_videos(request)
            
        except Exception as e:
            self.logger.error(f"Error getting trending videos: {e}")
            return SearchResponse(
                status=StatusEnum.ERROR,
                message=f"Failed to get trending videos: {str(e)}",
                query="trending"
            )
    
    def get_recent_videos(self, query: str, max_results: int = 10) -> SearchResponse:
        """
        Get recent videos for a specific query.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Search response with recent videos
        """
        try:
            request = SearchRequest(
                query=query,
                max_results=max_results,
                sort_by="upload_date",
                upload_date="week"  # Recent videos from this week
            )
            
            return self.search_videos(request)
            
        except Exception as e:
            self.logger.error(f"Error getting recent videos: {e}")
            return SearchResponse(
                status=StatusEnum.ERROR,
                message=f"Failed to get recent videos: {str(e)}",
                query=query
            )
    
    def suggest_videos(self, query: str, max_results: int = 5) -> List[str]:
        """
        Get video suggestions based on query.
        
        Args:
            query: Search query
            max_results: Maximum number of suggestions
            
        Returns:
            List of suggested video titles
        """
        try:
            request = SearchRequest(
                query=query,
                max_results=max_results,
                sort_by="relevance"
            )
            
            response = self.search_videos(request)
            if response.status == StatusEnum.SUCCESS:
                return [result.title for result in response.results]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting video suggestions: {e}")
            return [] 