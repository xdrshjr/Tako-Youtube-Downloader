"""
API routes for YouTube Downloader.
"""

from .video import router as video_router
from .search import router as search_router
from .batch import router as batch_router
from .config import router as config_router

__all__ = [
    "video_router",
    "search_router", 
    "batch_router",
    "config_router"
] 