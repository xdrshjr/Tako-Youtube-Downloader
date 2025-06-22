"""
Video-related API routes.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..services import DownloadService
from ..models.requests import VideoDownloadRequest, VideoInfoRequest
from ..models.responses import (
    VideoDownloadResponse,
    VideoInfoResponse,
    StatusEnum,
    HealthResponse
)

router = APIRouter(prefix="/api/v1/video", tags=["video"])

# Initialize service
download_service = DownloadService()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for video service."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.post("/info", response_model=VideoInfoResponse)
async def get_video_info(request: VideoInfoRequest):
    """
    Get information about a YouTube video without downloading it.
    
    Args:
        request: Video info request containing URL
        
    Returns:
        Video information response
    """
    try:
        response = download_service.get_video_info(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/download", response_model=VideoDownloadResponse)
async def download_video(request: VideoDownloadRequest):
    """
    Download a single YouTube video.
    
    Args:
        request: Video download request
        
    Returns:
        Video download response
    """
    try:
        response = download_service.download_video(request)
        
        if response.status == StatusEnum.ERROR:
            raise HTTPException(
                status_code=400,
                detail=response.message
            )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/download/{task_id}")
async def cancel_download(task_id: str) -> Dict[str, Any]:
    """
    Cancel an active video download.
    
    Args:
        task_id: Task ID to cancel
        
    Returns:
        Cancellation result
    """
    try:
        result = download_service.cancel_download(task_id)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=404,
                detail=result["message"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/downloads/active")
async def get_active_downloads() -> Dict[str, Any]:
    """
    Get list of active downloads.
    
    Returns:
        Active downloads information
    """
    try:
        return download_service.get_active_downloads()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 