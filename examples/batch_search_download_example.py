#!/usr/bin/env python3
"""
Batch Search Download Example

This example demonstrates how to use the YouTube Downloader's batch search
and download functionality to automatically search for videos and download
them based on specified criteria.

Usage:
    python batch_search_download_example.py
"""

import sys
import os
import time
from pathlib import Path

# Add src to path to import youtube_downloader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_downloader.core import (
    SearchEngine,
    SearchConfig,
    FilterConfig,
    VideoDownloader,
    DownloadConfig,
    BatchDownloadManager,
    BatchConfig,
    BatchProgress,
    BatchStatus
)


def progress_callback(progress: BatchProgress):
    """Progress callback function for batch downloads."""
    print(f"\r[{progress.status.value.upper()}] "
          f"Progress: {progress.overall_progress:.1f}% "
          f"({progress.completed_videos}/{progress.total_videos}) "
          f"Active: {progress.active_downloads} "
          f"Failed: {progress.failed_videos}", end="", flush=True)


def search_progress_callback(message: str):
    """Search progress callback function."""
    print(f"🔍 {message}")


def main():
    """Main example function."""
    print("🎬 YouTube Batch Search Download Example")
    print("=" * 50)
    
    # Configuration
    search_query = input("Enter search query (default: 'Python tutorial'): ").strip()
    if not search_query:
        search_query = "Python tutorial"
    
    try:
        max_results = int(input("Max results (default: 5): ") or "5")
        max_duration = int(input("Max duration in seconds (default: 600): ") or "600")
    except ValueError:
        max_results = 5
        max_duration = 600
    
    # Create output directory
    output_dir = Path("./test_downloads/batch_downloads")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📋 Configuration:")
    print(f"   Search Query: {search_query}")
    print(f"   Max Results: {max_results}")
    print(f"   Max Duration: {max_duration}s ({max_duration//60}m {max_duration%60}s)")
    print(f"   Output Directory: {output_dir.absolute()}")
    print()
    
    try:
        # Step 1: Create configurations
        print("⚙️  Setting up configurations...")
        
        # Filter configuration (more lenient for common searches)
        filter_config = FilterConfig(
            min_duration=10,              # At least 10 seconds (very lenient)
            max_duration=max_duration,    # User specified max duration
            exclude_shorts=False,         # Include YouTube Shorts for more results
            exclude_live=True,            # No live streams
            min_view_count=1000           # At least 1000 views for quality
        )
        
        # Search configuration
        search_config = SearchConfig(
            search_query=search_query,
            max_results=max_results,
            sort_by="view_count",         # Sort by view count
            filter_config=filter_config
        )
        
        # Download configuration
        download_config = DownloadConfig(
            output_directory=str(output_dir),
            quality="720p",               # Good quality balance
            format="mp4",                 # MP4 format
            audio_format="mp3"
        )
        
        # Batch configuration
        batch_config = BatchConfig(
            max_concurrent_downloads=2,   # 2 concurrent downloads
            retry_failed_downloads=True,
            max_retry_attempts=2,
            retry_delay=1.0
        )
        
        # Step 2: Search for videos
        print("🔍 Searching for videos...")
        search_engine = SearchEngine(search_config)
        
        videos = search_engine.search_videos(search_query)
        
        # Get filter statistics to help debug
        filter_summary = search_engine.video_filter.get_filter_summary()
        print(f"📊 Filter settings: {filter_summary}")
        
        # Add detailed debugging for raw search results
        print(f"🔍 Debug: Found {len(videos)} videos after filtering")
        
        if not videos:
            print("❌ No videos found matching the criteria.")
            print("💡 Tip: Try adjusting filter settings:")
            print("   - Increase max_duration for longer videos")
            print("   - Set exclude_shorts=False to include short videos")
            print("   - Lower min_view_count for less popular videos")
            print("   - Try a different search query")
            return
        
        print(f"✅ Found {len(videos)} videos:")
        for i, video in enumerate(videos, 1):
            duration_str = video.get_duration_formatted()
            print(f"   {i}. {video.title[:60]}... ({duration_str}) - {video.view_count:,} views")
        
        # Step 3: Set up batch downloader
        print(f"\n📥 Setting up batch downloader...")
        downloader = VideoDownloader(download_config)
        batch_manager = BatchDownloadManager(downloader, batch_config)
        
        # Set progress callback
        batch_manager.set_progress_callback(progress_callback)
        
        # Step 4: Add videos to queue
        print("📋 Adding videos to download queue...")
        batch_manager.add_to_queue(videos)
        
        print(f"✅ Added {len(videos)} videos to download queue")
        
        # Step 5: Start batch download
        print("\n🚀 Starting batch download...")
        print("Press Ctrl+C to cancel downloads\n")
        
        batch_manager.start_batch_download()
        
        # Wait for completion and show progress
        while True:
            progress = batch_manager.get_progress()
            
            if progress.status in [BatchStatus.COMPLETED, BatchStatus.CANCELLED, BatchStatus.ERROR]:
                break
            
            time.sleep(1)
        
        # Final results
        print("\n\n📊 Download Summary:")
        print("=" * 40)
        
        summary = batch_manager.get_batch_summary()
        final_progress = batch_manager.get_progress()
        
        print(f"Status: {final_progress.status.value.upper()}")
        print(f"Total Videos: {summary['total_videos']}")
        print(f"Completed: {summary['completed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.1f}s")
        print(f"Average Download Time: {summary['average_download_time']:.1f}s")
        
        # Show completed downloads
        completed_tasks = batch_manager.get_completed_tasks()
        if completed_tasks:
            print(f"\n✅ Successfully Downloaded:")
            for task in completed_tasks:
                if task.result and task.result.success:
                    print(f"   • {task.video.title[:50]}...")
                    if task.result.output_path:
                        print(f"     📁 {task.result.output_path}")
        
        # Show failed downloads
        failed_tasks = batch_manager.get_failed_tasks()
        if failed_tasks:
            print(f"\n❌ Failed Downloads:")
            for task in failed_tasks:
                print(f"   • {task.video.title[:50]}...")
                if task.error_message:
                    print(f"     💬 {task.error_message}")
        
        print(f"\n📁 Downloads saved to: {output_dir.absolute()}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Download cancelled by user")
        if 'batch_manager' in locals():
            batch_manager.cancel_download()
            print("🛑 Cancelling active downloads...")
            time.sleep(2)
    
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n👋 Example completed!")


def advanced_example():
    """
    Advanced example with more sophisticated filtering and error handling.
    """
    print("\n🎯 Advanced Batch Download Example")
    print("=" * 50)
    
    # More complex search configuration
    search_configs = [
        {
            "query": "Python machine learning tutorial",
            "max_results": 3,
            "min_duration": 10,   # 10 minutes
            "max_duration": 120,  # 1 hour
            "sort_by": "view_count"
        },
        {
            "query": "Data science Python",
            "max_results": 2,
            "min_duration": 10,   # 5 minutes
            "max_duration": 120,  # 30 minutes
            "sort_by": "upload_date"
        }
    ]
    
    output_dir = Path("./advanced_downloads")
    output_dir.mkdir(exist_ok=True)
    
    download_config = DownloadConfig(
        output_directory=str(output_dir),
        quality="best",
        format="mp4"
    )
    
    batch_config = BatchConfig(
        max_concurrent_downloads=1,  # Conservative for demo
        retry_failed_downloads=True,
        max_retry_attempts=1
    )
    
    # Initialize components
    downloader = VideoDownloader(download_config)
    batch_manager = BatchDownloadManager(downloader, batch_config)
    batch_manager.set_progress_callback(progress_callback)
    
    total_videos = 0
    
    # Search and queue videos from multiple queries
    for config in search_configs:
        print(f"\n🔍 Searching: {config['query']}")
        
        filter_config = FilterConfig(
            min_duration=config["min_duration"],
            max_duration=config["max_duration"],
            exclude_shorts=True,
            exclude_live=True,
            min_view_count=5000
        )
        
        search_config = SearchConfig(
            search_query=config["query"],
            max_results=config["max_results"],
            sort_by=config["sort_by"],
            filter_config=filter_config
        )
        
        search_engine = SearchEngine(search_config)
        videos = search_engine.search_videos(config["query"])
        
        if videos:
            batch_manager.add_to_queue(videos)
            total_videos += len(videos)
            print(f"   ✅ Added {len(videos)} videos")
        else:
            print(f"   ⚠️  No videos found")
    
    if total_videos > 0:
        print(f"\n🚀 Starting download of {total_videos} videos...")
        batch_manager.start_batch_download()
        
        # Wait for completion
        while True:
            progress = batch_manager.get_progress()
            if progress.status in [BatchStatus.COMPLETED, BatchStatus.CANCELLED]:
                break
            time.sleep(1)
        
        print(f"\n✅ Advanced example completed!")
        summary = batch_manager.get_batch_summary()
        print(f"   Success rate: {summary['success_rate']:.1f}%")
    else:
        print("❌ No videos to download")


if __name__ == "__main__":
    main()
    
    # Uncomment to run advanced example
    # advanced_example() 