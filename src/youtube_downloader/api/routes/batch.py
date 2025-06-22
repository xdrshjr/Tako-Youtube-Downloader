"""
Batch download-related API routes.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..services import BatchService
from ..models.requests import BatchDownloadRequest
from ..models.responses import (
    BatchDownloadResponse,
    BatchProgressResponse,
    StatusEnum
)

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])

# Initialize service
batch_service = BatchService()


@router.post("/download", response_model=BatchDownloadResponse)
async def start_batch_download(request: BatchDownloadRequest):
    """
    Start a batch download operation.
    
    Args:
        request: Batch download request with URLs and settings
        
    Returns:
        Batch download response with task ID
    """
    try:
        response = batch_service.start_batch_download(request)
        
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


@router.get("/progress/{task_id}", response_model=BatchProgressResponse)
async def get_batch_progress(task_id: str):
    """
    Get progress information for a batch download.
    
    Args:
        task_id: Batch download task ID
        
    Returns:
        Batch progress response
    """
    try:
        response = batch_service.get_batch_progress(task_id)
        
        if response.status == StatusEnum.ERROR and "not found" in response.message:
            raise HTTPException(
                status_code=404,
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
async def cancel_batch_download(task_id: str) -> Dict[str, Any]:
    """
    Cancel a batch download operation.
    
    Args:
        task_id: Batch download task ID to cancel
        
    Returns:
        Cancellation result
    """
    try:
        result = batch_service.cancel_batch_download(task_id)
        
        if result["status"] == "error":
            if "not found" in result["message"]:
                raise HTTPException(
                    status_code=404,
                    detail=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=400,
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


@router.get("/active")
async def get_active_batches() -> Dict[str, Any]:
    """
    Get list of active batch downloads.
    
    Returns:
        Active batch downloads information
    """
    try:
        return batch_service.get_active_batches()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 