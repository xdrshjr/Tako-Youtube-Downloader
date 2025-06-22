#!/usr/bin/env python3
"""
YouTube Downloader API Usage Example

This example demonstrates how to use the YouTube Downloader FastAPI service
for various operations like searching videos, downloading single videos,
and batch downloading.

Prerequisites:
1. Start the API server: python start_api.py
2. Install requests: pip install requests

Usage:
    python examples/api_usage_example.py
"""

import requests
import time
import json
from typing import Dict, Any


# API Base URL (adjust if your server runs on different host/port)
API_BASE_URL = "http://localhost:8000"


class YouTubeDownloaderAPI:
    """Client for YouTube Downloader API."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize the API client."""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get information about a YouTube video."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/video/info",
                json={"url": url}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def download_video(self, url: str, quality: str = "best", 
                      format: str = "mp4", output_dir: str = "./downloads") -> Dict[str, Any]:
        """Download a single video."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/video/download",
                json={
                    "url": url,
                    "quality": quality,
                    "format": format,
                    "output_directory": output_dir
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def search_videos(self, query: str, max_results: int = 10, 
                     min_duration: int = None, max_duration: int = None) -> Dict[str, Any]:
        """Search for YouTube videos."""
        try:
            search_data = {
                "query": query,
                "max_results": max_results
            }
            if min_duration:
                search_data["min_duration"] = min_duration
            if max_duration:
                search_data["max_duration"] = max_duration
            
            response = self.session.post(
                f"{self.base_url}/api/v1/search/videos",
                json=search_data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def batch_download(self, urls: list, quality: str = "best", 
                      format: str = "mp4") -> Dict[str, Any]:
        """Start a batch download operation."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/batch/download",
                json={
                    "urls": urls,
                    "quality": quality,
                    "format": format,
                    "max_concurrent_downloads": 2
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def get_batch_progress(self, task_id: str) -> Dict[str, Any]:
        """Get progress of a batch download."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/batch/progress/{task_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/config/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


def print_json(data: Dict[str, Any], title: str = ""):
    """Pretty print JSON data."""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    print(json.dumps(data, indent=2))


def main():
    """Main example function."""
    print("🎬 YouTube Downloader API Usage Example")
    print("=" * 50)
    
    # Initialize API client
    api = YouTubeDownloaderAPI()
    
    # 1. Health Check
    print("\n1. 🏥 Health Check")
    health = api.health_check()
    if "error" in health:
        print(f"❌ API server is not running: {health['error']}")
        print("Please start the server first: python start_api.py")
        return
    print("✅ API server is healthy")
    print_json(health)
    
    # 2. Get Configuration
    print("\n2. ⚙️ Get Configuration")
    config = api.get_config()
    print_json(config, "Current Configuration")
    
    # 3. Video Information Example
    print("\n3. 📹 Get Video Information")
    example_url = input("Enter a YouTube URL (or press Enter for example): ").strip()
    if not example_url:
        example_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll example
    
    video_info = api.get_video_info(example_url)
    print_json(video_info, f"Video Info for: {example_url}")
    
    # 4. Search Videos Example
    print("\n4. 🔍 Search Videos")
    search_query = input("Enter search query (or press Enter for 'Python tutorial'): ").strip()
    if not search_query:
        search_query = "Python tutorial"
    
    search_results = api.search_videos(
        query=search_query,
        max_results=5,
        min_duration=60,  # At least 1 minute
        max_duration=1800  # At most 30 minutes
    )
    print_json(search_results, f"Search Results for: {search_query}")
    
    # 5. Single Video Download Example (optional)
    print("\n5. 📥 Single Video Download")
    download_choice = input("Do you want to download the example video? (y/N): ").strip().lower()
    if download_choice == 'y':
        print("Starting download...")
        download_result = api.download_video(
            url=example_url,
            quality="720p",
            format="mp4"
        )
        print_json(download_result, "Download Result")
    else:
        print("Skipped download")
    
    # 6. Batch Download Example (optional)
    print("\n6. 📦 Batch Download")
    if "results" in search_results and search_results["results"]:
        batch_choice = input("Do you want to start a batch download of search results? (y/N): ").strip().lower()
        if batch_choice == 'y':
            # Get first 3 URLs from search results
            urls = [result["url"] for result in search_results["results"][:3]]
            print(f"Starting batch download of {len(urls)} videos...")
            
            batch_result = api.batch_download(urls, quality="720p")
            print_json(batch_result, "Batch Download Started")
            
            if "task_id" in batch_result:
                task_id = batch_result["task_id"]
                print(f"\n📊 Monitoring batch progress (Task ID: {task_id})")
                
                # Monitor progress for a few iterations
                for i in range(10):
                    time.sleep(2)
                    progress = api.get_batch_progress(task_id)
                    if progress.get("status") == "completed":
                        print_json(progress, "Final Progress")
                        break
                    elif progress.get("status") == "error":
                        print_json(progress, "Error in Batch Download")
                        break
                    else:
                        overall_progress = progress.get("overall_progress", 0)
                        print(f"Progress: {overall_progress:.1f}%")
        else:
            print("Skipped batch download")
    
    print("\n✅ Example completed!")
    print("\n📖 More API endpoints:")
    print("   - GET /api/v1/info - API information")
    print("   - GET /docs - Interactive API documentation")
    print("   - GET /redoc - Alternative API documentation")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}") 