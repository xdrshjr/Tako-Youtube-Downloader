"""
API routes package.
"""

from .video import router as video_router
from .search import router as search_router
from .batch import router as batch_router
from .config import router as config_router
from .download import router as download_router

__all__ = [
    "video_router",
    "search_router", 
    "batch_router",
    "config_router",
    "download_router"
] 