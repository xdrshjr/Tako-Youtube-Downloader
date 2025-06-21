"""
Main entry point for YouTube Downloader.

Provides a simple command-line interface for downloading YouTube videos.
"""

import sys
import argparse
import logging
from pathlib import Path

from .core.validator import URLValidator
from .core.downloader import VideoDownloader
from .core.config import ConfigManager, DownloadConfig


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('downloader.log')
        ]
    )


def progress_callback(data: dict) -> None:
    """
    Simple progress callback for displaying download progress.
    
    Args:
        data: Progress data from yt-dlp
    """
    if data['status'] == 'downloading':
        if 'total_bytes' in data and data['total_bytes']:
            percent = (data['downloaded_bytes'] / data['total_bytes']) * 100
            print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
        elif '_percent_str' in data:
            print(f"\rDownloading: {data['_percent_str']}", end='', flush=True)
    elif data['status'] == 'finished':
        print("\nDownload completed!")


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="YouTube Video Downloader - Download videos from YouTube"
    )
    
    parser.add_argument(
        "url",
        help="YouTube video URL to download"
    )
    
    parser.add_argument(
        "-q", "--quality",
        choices=["best", "worst", "720p", "1080p", "480p", "360p"],
        default="best",
        help="Video quality to download (default: best)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["mp4", "webm", "mkv"],
        default="mp4",
        help="Output format (default: mp4)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="./downloads",
        help="Output directory (default: ./downloads)"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Only show video information, don't download"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Step 1: Validate URL
        logger.info(f"Validating URL: {args.url}")
        validator = URLValidator()
        
        if not validator.validate_youtube_url(args.url):
            logger.error("Invalid YouTube URL provided")
            print("Error: Invalid YouTube URL. Please provide a valid YouTube video URL.")
            sys.exit(1)
        
        video_id = validator.extract_video_id(args.url)
        normalized_url = validator.normalize_url(args.url)
        
        logger.info(f"URL validated successfully. Video ID: {video_id}")
        print(f"Video ID: {video_id}")
        print(f"Normalized URL: {normalized_url}")
        
        # Step 2: Load configuration
        if args.config:
            logger.info(f"Loading configuration from: {args.config}")
            config_manager = ConfigManager(config_file=args.config)
        else:
            logger.info("Using default configuration")
            config_manager = ConfigManager()
        
        config = config_manager.get_config()
        
        # Override config with command line arguments
        if args.quality != "best":
            config.quality = args.quality
        if args.format != "mp4":
            config.format = args.format
        if args.output != "./downloads":
            config.output_directory = args.output
        
        logger.info(f"Configuration: Quality={config.quality}, Format={config.format}, Output={config.output_directory}")
        
        # Step 3: Initialize downloader
        downloader = VideoDownloader(config)
        downloader.set_progress_callback(progress_callback)
        
        # Step 4: Get video information
        logger.info("Fetching video information...")
        print("Fetching video information...")
        
        try:
            video_info = downloader.get_video_info(args.url)
            
            print(f"\nVideo Information:")
            print(f"  Title: {video_info.title}")
            print(f"  Uploader: {video_info.uploader}")
            print(f"  Duration: {video_info.duration} seconds")
            print(f"  Upload Date: {video_info.upload_date}")
            print(f"  View Count: {video_info.view_count:,}")
            if video_info.like_count:
                print(f"  Like Count: {video_info.like_count:,}")
            print()
            
        except Exception as e:
            logger.error(f"Failed to fetch video information: {e}")
            print(f"Error: Could not fetch video information. {e}")
            sys.exit(1)
        
        # Step 5: Download video (unless info-only mode)
        if args.info_only:
            print("Info-only mode: Skipping download.")
            return
        
        logger.info("Starting video download...")
        print("Starting download...")
        
        result = downloader.download_video(args.url)
        
        # Step 6: Display results
        if result.success:
            logger.info(f"Download completed successfully: {result.output_path}")
            print(f"\nDownload completed successfully!")
            print(f"Output path: {result.output_path}")
            if result.file_size:
                file_size_mb = result.file_size / (1024 * 1024)
                print(f"File size: {file_size_mb:.2f} MB")
        else:
            logger.error(f"Download failed: {result.error_message}")
            print(f"\nDownload failed: {result.error_message}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Download cancelled by user")
        print("\nDownload cancelled by user.")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 