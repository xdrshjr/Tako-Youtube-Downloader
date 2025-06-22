"""
Download status-related API routes.
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..services import DownloadService
from ..models.responses import DownloadStatusResponse, StatusEnum

router = APIRouter(prefix="/api/v1/download", tags=["download"])

# Initialize service
download_service = DownloadService()


@router.get("/status/{task_id}", response_model=DownloadStatusResponse)
async def get_download_status(task_id: str):
    """
    Get the status of a download task.
    
    Args:
        task_id: Task ID to check status for
        
    Returns:
        Download status response
    """
    try:
        response = download_service.get_download_status(task_id)
        
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


@router.get("/file/{task_id}")
async def download_file(task_id: str):
    """
    Download the completed file for a task.
    
    Args:
        task_id: Task ID to download file for
        
    Returns:
        File response with the downloaded video
    """
    try:
        # First check if task exists and get file path
        status_response = download_service.get_download_status(task_id)
        
        if status_response.status == StatusEnum.ERROR:
            # Task not found in memory, try to find file in downloads directory
            downloads_dir = Path("./downloads")
            
            # Look for files with task_id in the name
            matching_files = list(downloads_dir.glob(f"*{task_id}*"))
            if not matching_files:
                # Also try looking for recent files (last 24 hours) as fallback
                import time
                current_time = time.time()
                recent_files = [
                    f for f in downloads_dir.glob("*") 
                    if f.is_file() and (current_time - f.stat().st_mtime) < 86400  # 24 hours
                ]
                if not recent_files:
                    raise HTTPException(
                        status_code=404,
                        detail=f"File for task {task_id} not found. Task may have been cleaned up or file moved."
                    )
                # Use most recent file as best guess
                file_path = max(recent_files, key=lambda f: f.stat().st_mtime)
            else:
                file_path = matching_files[0]  # Use first match
        else:
            # Task found, use the output path
            if not status_response.output_path:
                raise HTTPException(
                    status_code=404,
                    detail=f"No file path available for task {task_id}"
                )
            file_path = Path(status_response.output_path)
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_path}"
            )
        
        # Determine filename for download
        filename = file_path.name
        if status_response and status_response.status != StatusEnum.ERROR and status_response.video_title:
            # Use video title if available
            safe_title = "".join(c for c in status_response.video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            file_extension = file_path.suffix
            filename = f"{safe_title}{file_extension}"
        
        # Return file response
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 