"""
Configuration-related API routes.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ...core import ConfigManager
from ..models.requests import ConfigUpdateRequest
from ..models.responses import ConfigResponse, StatusEnum

router = APIRouter(prefix="/api/v1/config", tags=["config"])

# Initialize config manager
config_manager = ConfigManager()


@router.get("/", response_model=ConfigResponse)
async def get_config():
    """Get current configuration settings."""
    try:
        config = config_manager.get_config()
        
        config_dict = {
            "quality": config.quality,
            "format": config.format,
            "output_directory": config.output_directory,
            "audio_format": config.audio_format
        }
        
        return ConfigResponse(
            status=StatusEnum.SUCCESS,
            message="Configuration retrieved successfully",
            config=config_dict
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/defaults")
async def get_default_config() -> Dict[str, Any]:
    """Get default configuration values."""
    return {
        "quality_options": ["best", "worst", "720p", "1080p", "480p", "360p"],
        "format_options": ["mp4", "webm", "mkv"],
        "audio_format_options": ["mp3", "aac", "opus"],
        "defaults": {
            "quality": "best",
            "format": "mp4",
            "output_directory": "./downloads",
            "audio_format": "mp3"
        }
    } 