"""
Search-related API routes.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List

from ..services import SearchService
from ..models.requests import SearchRequest
from ..models.responses import SearchResponse

router = APIRouter(prefix="/api/v1/search", tags=["search"])

# Initialize service
search_service = SearchService()


@router.post("/videos", response_model=SearchResponse)
async def search_videos(request: SearchRequest):
    """
    Search for YouTube videos based on query and filters.
    
    Args:
        request: Search request with query and filters
        
    Returns:
        Search response with video results
    """
    try:
        response = search_service.search_videos(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/trending", response_model=SearchResponse)
async def get_trending_videos(
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=50)
):
    """
    Get trending YouTube videos.
    
    Args:
        max_results: Maximum number of results to return
        
    Returns:
        Search response with trending videos
    """
    try:
        response = search_service.get_trending_videos(max_results)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/recent", response_model=SearchResponse)
async def get_recent_videos(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=50)
):
    """
    Get recent YouTube videos for a specific query.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Search response with recent videos
    """
    try:
        response = search_service.get_recent_videos(query, max_results)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/suggestions")
async def get_video_suggestions(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, description="Maximum number of suggestions", ge=1, le=20)
) -> List[str]:
    """
    Get video title suggestions based on query.
    
    Args:
        query: Search query
        max_results: Maximum number of suggestions to return
        
    Returns:
        List of suggested video titles
    """
    try:
        suggestions = search_service.suggest_videos(query, max_results)
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 