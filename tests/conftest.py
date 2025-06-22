"""
Test configuration and fixtures for YouTube Downloader.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))


@pytest.fixture
def api_client():
    """FastAPI test client."""
    from youtube_downloader.api.main import app
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_video_url():
    """Sample YouTube video URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 