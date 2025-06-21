"""
Integrated batch search downloader module for YouTube Downloader.

This module provides a high-level interface that combines search functionality
with batch download management for a complete search-to-download workflow.
"""

import logging
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass

from .search_engine import SearchEngine, SearchError
from .batch_manager import BatchDownloadManager, BatchProgress, BatchConfig
from .video_filter import VideoSearchResult
from .search_config import SearchConfig, FilterConfig
from .downloader import VideoDownloader
from .config import DownloadConfig


@dataclass
class BatchSearchConfig:
    """
    Configuration for batch search and download operations.
    """
    # Search parameters
    search_query: str
    max_results: int = 10
    sort_by: str = "relevance"  # "relevance", "upload_date", "view_count", "rating"
    upload_date: str = "any"    # "hour", "today", "week", "month", "year", "any"
    
    # Filter parameters
    min_duration: Optional[int] = None      # seconds
    max_duration: Optional[int] = None      # seconds
    min_view_count: Optional[int] = None
    exclude_shorts: bool = True
    exclude_live: bool = True
    min_upload_date: Optional[str] = None   # ISO format
    
    # Batch download parameters
    max_concurrent_downloads: int = 3
    retry_failed_downloads: bool = True
    max_retry_attempts: int = 3
    retry_delay: float = 2.0
    stop_on_first_error: bool = False
    
    def to_search_config(self) -> SearchConfig:
        """Convert to SearchConfig."""
        filter_config = FilterConfig(
            min_duration=self.min_duration,
            max_duration=self.max_duration,
            min_view_count=self.min_view_count,
            exclude_shorts=self.exclude_shorts,
            exclude_live=self.exclude_live,
            min_upload_date=self.min_upload_date
        )
        
        return SearchConfig(
            search_query=self.search_query,
            max_results=self.max_results,
            sort_by=self.sort_by,
            upload_date=self.upload_date,
            filter_config=filter_config
        )
    
    def to_batch_config(self) -> BatchConfig:
        """Convert to BatchConfig."""
        return BatchConfig(
            max_concurrent_downloads=self.max_concurrent_downloads,
            retry_failed_downloads=self.retry_failed_downloads,
            max_retry_attempts=self.max_retry_attempts,
            retry_delay=self.retry_delay,
            stop_on_first_error=self.stop_on_first_error
        )


@dataclass
class BatchSearchResult:
    """
    Result of batch search and download operation.
    """
    search_query: str
    total_found: int
    total_filtered: int
    videos_queued: int
    search_time: float
    filter_summary: Dict[str, Any]


class BatchSearchDownloadError(Exception):
    """Exception for batch search download errors."""
    pass


class BatchSearchDownloader:
    """
    Integrated batch search and downloader.
    
    Provides a high-level interface for searching YouTube videos and 
    batch downloading them with comprehensive filtering and progress tracking.
    
    Features:
    - One-stop search to download functionality
    - Intelligent video filtering
    - Real-time progress tracking
    - Error handling and recovery
    - Configurable download parameters
    """
    
    def __init__(self, download_config: DownloadConfig):
        """
        Initialize the batch search downloader.
        
        Args:
            download_config: Configuration for video downloading
        """
        self.download_config = download_config
        
        # Initialize core components (will be created per operation)
        self._search_engine: Optional[SearchEngine] = None
        self._batch_manager: Optional[BatchDownloadManager] = None
        self._downloader: Optional[VideoDownloader] = None
        
        # Progress and callback management
        self._progress_callback: Optional[Callable[[BatchProgress], None]] = None
        self._search_progress_callback: Optional[Callable[[str], None]] = None
        
        # Logging
        self._logger = logging.getLogger(__name__)
        
        self._logger.info("BatchSearchDownloader initialized", extra={
            'output_directory': download_config.output_directory,
            'quality': download_config.quality,
            'format': download_config.format
        })
    
    def search_and_download(self, config: BatchSearchConfig) -> BatchSearchResult:
        """
        Search for videos and add them to download queue.
        
        Args:
            config: Batch search configuration
            
        Returns:
            BatchSearchResult: Summary of search and queue operation
            
        Raises:
            BatchSearchDownloadError: If search or queue operation fails
        """
        import time
        
        start_time = time.time()
        
        try:
            # Initialize components
            self._initialize_components(config)
            
            # Perform search
            self._logger.info(f"Starting search for: '{config.search_query}'")
            
            if self._search_progress_callback:
                self._search_progress_callback(f"Searching for: {config.search_query}")
            
            search_config = config.to_search_config()
            videos = self._search_engine.search_videos(config.search_query, config.max_results)
            
            search_time = time.time() - start_time
            
            self._logger.info(f"Search completed", extra={
                'query': config.search_query,
                'found_videos': len(videos),
                'search_time': search_time
            })
            
            if not videos:
                self._logger.warning("No videos found matching search criteria")
                return BatchSearchResult(
                    search_query=config.search_query,
                    total_found=0,
                    total_filtered=0,
                    videos_queued=0,
                    search_time=search_time,
                    filter_summary={}
                )
            
            # Add videos to download queue
            if self._search_progress_callback:
                self._search_progress_callback(f"Adding {len(videos)} videos to download queue")
            
            self._batch_manager.add_to_queue(videos, self.download_config)
            
            # Get filter summary
            filter_summary = self._search_engine.video_filter.get_filter_summary()
            
            result = BatchSearchResult(
                search_query=config.search_query,
                total_found=len(videos),  # After filtering
                total_filtered=len(videos),
                videos_queued=len(videos),
                search_time=search_time,
                filter_summary=filter_summary
            )
            
            self._logger.info(f"Videos added to download queue", extra={
                'queued_count': len(videos),
                'queue_size': self._batch_manager.get_queue_size()
            })
            
            return result
            
        except SearchError as e:
            self._logger.error(f"Search failed: {str(e)}")
            raise BatchSearchDownloadError(f"Search failed: {str(e)}")
        except Exception as e:
            self._logger.error(f"Batch search operation failed: {str(e)}")
            raise BatchSearchDownloadError(f"Batch search operation failed: {str(e)}")
    
    def start_downloads(self) -> None:
        """
        Start the batch download process.
        
        Raises:
            BatchSearchDownloadError: If download cannot be started
        """
        if not self._batch_manager:
            raise BatchSearchDownloadError("No batch manager initialized. Run search_and_download first.")
        
        try:
            self._logger.info("Starting batch downloads")
            self._batch_manager.start_batch_download()
        except Exception as e:
            self._logger.error(f"Failed to start downloads: {str(e)}")
            raise BatchSearchDownloadError(f"Failed to start downloads: {str(e)}")
    
    def pause_downloads(self) -> None:
        """Pause the batch download process."""
        if self._batch_manager:
            self._batch_manager.pause_download()
        else:
            self._logger.warning("No active batch manager to pause")
    
    def resume_downloads(self) -> None:
        """Resume the batch download process."""
        if self._batch_manager:
            self._batch_manager.resume_download()
        else:
            self._logger.warning("No active batch manager to resume")
    
    def cancel_downloads(self) -> None:
        """Cancel the batch download process."""
        if self._batch_manager:
            self._batch_manager.cancel_download()
        else:
            self._logger.warning("No active batch manager to cancel")
    
    def get_download_progress(self) -> Optional[BatchProgress]:
        """
        Get current download progress.
        
        Returns:
            BatchProgress: Current progress or None if no downloads active
        """
        if self._batch_manager:
            return self._batch_manager.get_progress()
        return None
    
    def get_batch_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive batch download summary.
        
        Returns:
            Dict containing detailed batch statistics or None if no downloads active
        """
        if self._batch_manager:
            return self._batch_manager.get_batch_summary()
        return None
    
    def set_progress_callback(self, callback: Callable[[BatchProgress], None]) -> None:
        """
        Set callback for download progress updates.
        
        Args:
            callback: Function to call when download progress is updated
        """
        self._progress_callback = callback
        if self._batch_manager:
            self._batch_manager.set_progress_callback(callback)
    
    def set_search_progress_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set callback for search progress updates.
        
        Args:
            callback: Function to call with search status messages
        """
        self._search_progress_callback = callback
    
    def search_and_download_auto(self, config: BatchSearchConfig) -> Dict[str, Any]:
        """
        Perform complete search and download operation automatically.
        
        Args:
            config: Batch search configuration
            
        Returns:
            Dict containing operation summary
            
        Raises:
            BatchSearchDownloadError: If operation fails
        """
        try:
            # Perform search and add to queue
            search_result = self.search_and_download(config)
            
            if search_result.videos_queued == 0:
                return {
                    'search_result': search_result,
                    'download_summary': None,
                    'status': 'no_videos_found'
                }
            
            # Start downloads automatically
            self.start_downloads()
            
            # Return initial summary
            return {
                'search_result': search_result,
                'download_summary': self.get_batch_summary(),
                'status': 'downloads_started'
            }
            
        except Exception as e:
            self._logger.error(f"Auto operation failed: {str(e)}")
            raise BatchSearchDownloadError(f"Auto operation failed: {str(e)}")
    
    def _initialize_components(self, config: BatchSearchConfig) -> None:
        """
        Initialize search engine and batch manager components.
        
        Args:
            config: Batch search configuration
        """
        # Initialize downloader
        self._downloader = VideoDownloader(self.download_config)
        
        # Initialize search engine
        search_config = config.to_search_config()
        self._search_engine = SearchEngine(search_config)
        
        # Initialize batch manager
        batch_config = config.to_batch_config()
        self._batch_manager = BatchDownloadManager(self._downloader, batch_config)
        
        # Set progress callback if available
        if self._progress_callback:
            self._batch_manager.set_progress_callback(self._progress_callback)
        
        self._logger.debug("Components initialized", extra={
            'search_query': config.search_query,
            'max_results': config.max_results,
            'max_concurrent': config.max_concurrent_downloads
        })


# Convenience function for quick usage
def quick_batch_download(
    search_query: str,
    max_results: int = 10,
    output_directory: str = "./downloads",
    quality: str = "best",
    max_duration: Optional[int] = None,
    min_duration: Optional[int] = None,
    exclude_shorts: bool = True,
    max_concurrent: int = 3,
    progress_callback: Optional[Callable[[BatchProgress], None]] = None
) -> Dict[str, Any]:
    """
    Quick batch download function for simple use cases.
    
    Args:
        search_query: YouTube search query
        max_results: Maximum number of videos to download
        output_directory: Directory to save downloaded videos
        quality: Video quality preference
        max_duration: Maximum video duration in seconds
        min_duration: Minimum video duration in seconds
        exclude_shorts: Whether to exclude YouTube Shorts
        max_concurrent: Maximum concurrent downloads
        progress_callback: Optional progress callback function
        
    Returns:
        Dict containing operation summary
        
    Example:
        >>> result = quick_batch_download(
        ...     search_query="Python tutorial",
        ...     max_results=5,
        ...     max_duration=1800,  # 30 minutes
        ...     exclude_shorts=True
        ... )
        >>> print(f"Downloaded {result['search_result'].videos_queued} videos")
    """
    # Create download configuration
    download_config = DownloadConfig(
        output_directory=output_directory,
        quality=quality,
        format="mp4"
    )
    
    # Create batch search configuration
    batch_config = BatchSearchConfig(
        search_query=search_query,
        max_results=max_results,
        max_duration=max_duration,
        min_duration=min_duration,
        exclude_shorts=exclude_shorts,
        max_concurrent_downloads=max_concurrent
    )
    
    # Create and execute batch downloader
    downloader = BatchSearchDownloader(download_config)
    
    if progress_callback:
        downloader.set_progress_callback(progress_callback)
    
    return downloader.search_and_download_auto(batch_config) 