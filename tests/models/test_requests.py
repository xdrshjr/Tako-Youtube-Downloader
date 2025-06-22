# Tests for request models
import pytest
from pydantic import ValidationError


def test_video_info_request():
    """Test VideoInfoRequest model."""
    from youtube_downloader.api.models.requests import VideoInfoRequest
    
    # Valid request
    request = VideoInfoRequest(url="https://www.youtube.com/watch?v=test")
    assert request.url == "https://www.youtube.com/watch?v=test"
    
    # Invalid request (missing URL)
    with pytest.raises(ValidationError):
        VideoInfoRequest()


def test_video_download_request():
    """Test VideoDownloadRequest model."""
    from youtube_downloader.api.models.requests import VideoDownloadRequest
    
    # Valid request
    request = VideoDownloadRequest(url="https://www.youtube.com/watch?v=test")
    assert request.url == "https://www.youtube.com/watch?v=test"
    assert request.quality == "best"  # Default value
    
    # Invalid request (missing URL)
    with pytest.raises(ValidationError):
        VideoDownloadRequest()


def test_search_request():
    """Test SearchRequest model."""
    from youtube_downloader.api.models.requests import SearchRequest
    
    # Valid request
    request = SearchRequest(query="Python tutorial")
    assert request.query == "Python tutorial"
    assert request.max_results == 10  # Default value
    
    # Invalid request (missing query)
    with pytest.raises(ValidationError):
        SearchRequest() 