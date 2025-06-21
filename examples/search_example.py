#!/usr/bin/env python3
"""
YouTube Batch Search Download Example

This example demonstrates how to use the new search functionality to:
1. Search for YouTube videos using keywords
2. Apply filters (duration, view count, etc.)
3. Get filtered results for batch downloading

Usage:
    python search_example.py
"""

import sys
import logging
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_downloader.core import (
    SearchEngine,
    SearchConfig,
    FilterConfig,
    SearchConfigManager,
    VideoSearchResult
)


def setup_logging():
    """Setup logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('search_example.log')
        ]
    )


def basic_search_example():
    """Demonstrate basic video search functionality."""
    print("=" * 60)
    print("BASIC SEARCH EXAMPLE")
    print("=" * 60)
    
    # Create basic search configuration
    config = SearchConfig(
        search_query="Python programming tutorial",
        max_results=5,
        sort_by="relevance"
    )
    
    # Initialize search engine
    engine = SearchEngine(config)
    
    try:
        # Perform search
        print(f"Searching for: '{config.search_query}'")
        print(f"Maximum results: {config.max_results}")
        print("Searching...")
        
        results = engine.search_videos(config.search_query)
        
        print(f"\nFound {len(results)} videos after filtering:")
        print("-" * 40)
        
        for i, video in enumerate(results, 1):
            print(f"{i}. {video.title}")
            print(f"   Channel: {video.uploader}")
            print(f"   Duration: {video.get_duration_formatted()}")
            print(f"   Views: {video.view_count:,}")
            print(f"   Upload Date: {video.upload_date}")
            print(f"   URL: {video.get_url()}")
            print()
            
    except Exception as e:
        print(f"Search failed: {e}")


def advanced_filtering_example():
    """Demonstrate advanced filtering capabilities."""
    print("=" * 60)
    print("ADVANCED FILTERING EXAMPLE")
    print("=" * 60)
    
    # Create advanced filter configuration
    filter_config = FilterConfig(
        min_duration=300,      # At least 5 minutes
        max_duration=1800,     # At most 30 minutes
        min_view_count=10000,  # At least 10k views
        exclude_shorts=True,   # No YouTube Shorts
        exclude_live=True,     # No live streams
        min_upload_date="2023-01-01"  # Only recent videos
    )
    
    config = SearchConfig(
        search_query="machine learning explained",
        max_results=10,
        sort_by="view_count",
        upload_date="year",  # Only videos from last year
        filter_config=filter_config
    )
    
    engine = SearchEngine(config)
    
    try:
        print("Search Configuration:")
        print(f"  Query: '{config.search_query}'")
        print(f"  Max Results: {config.max_results}")
        print(f"  Sort By: {config.sort_by}")
        print(f"  Upload Date Filter: {config.upload_date}")
        print("\nFilter Configuration:")
        print(f"  Duration: {filter_config.min_duration}s - {filter_config.max_duration}s")
        print(f"  Min Views: {filter_config.min_view_count:,}")
        print(f"  Exclude Shorts: {filter_config.exclude_shorts}")
        print(f"  Exclude Live: {filter_config.exclude_live}")
        print(f"  Min Upload Date: {filter_config.min_upload_date}")
        print("\nSearching...")
        
        results = engine.search_videos(config.search_query)
        
        print(f"\nFiltered Results: {len(results)} videos")
        print("-" * 50)
        
        for i, video in enumerate(results, 1):
            duration_formatted = video.get_duration_formatted()
            print(f"{i}. {video.title[:60]}...")
            print(f"   📺 {video.uploader}")
            print(f"   ⏱️  {duration_formatted} | 👁️  {video.view_count:,} views")
            print(f"   📅 {video.upload_date}")
            print(f"   🔗 {video.get_url()}")
            print()
            
    except Exception as e:
        print(f"Advanced search failed: {e}")


def search_config_manager_example():
    """Demonstrate SearchConfigManager usage."""
    print("=" * 60)
    print("SEARCH CONFIG MANAGER EXAMPLE")
    print("=" * 60)
    
    # Initialize config manager
    manager = SearchConfigManager()
    
    # Update configuration dynamically
    manager.update_config(
        search_query="data science tutorial",
        max_results=8,
        sort_by="upload_date",
        filter_min_duration=600,    # At least 10 minutes
        filter_max_duration=3600,   # At most 1 hour
        filter_exclude_shorts=True,
        filter_min_view_count=5000
    )
    
    config = manager.get_config()
    engine = SearchEngine(config)
    
    try:
        print("Configuration Summary:")
        stats = engine.get_search_statistics()
        
        print("Search Parameters:")
        for key, value in stats['config'].items():
            print(f"  {key}: {value}")
        
        print("\nFilter Summary:")
        for key, value in stats['filters'].items():
            if value is not None:
                print(f"  {key}: {value}")
        
        print(f"\nExecuting search for: '{config.search_query}'")
        results = engine.search_videos(config.search_query)
        
        print(f"\nResults: {len(results)} videos found")
        
        # Show summary statistics
        if results:
            total_duration = sum(video.duration for video in results)
            avg_views = sum(video.view_count for video in results) / len(results)
            
            print("\nSummary Statistics:")
            print(f"  Total Duration: {total_duration // 60} minutes")
            print(f"  Average Views: {avg_views:,.0f}")
            print(f"  Shortest Video: {min(video.duration for video in results)}s")
            print(f"  Longest Video: {max(video.duration for video in results)}s")
            
    except Exception as e:
        print(f"Config manager example failed: {e}")


def filter_analysis_example():
    """Demonstrate filter analysis capabilities."""
    print("=" * 60)
    print("FILTER ANALYSIS EXAMPLE")
    print("=" * 60)
    
    # Create a configuration for analysis
    filter_config = FilterConfig(
        min_duration=120,
        min_view_count=1000,
        exclude_shorts=True
    )
    
    config = SearchConfig(
        search_query="python basics",
        max_results=15,
        filter_config=filter_config
    )
    
    engine = SearchEngine(config)
    
    try:
        print(f"Analyzing filters for query: '{config.search_query}'")
        
        # Note: This would require access to raw results before filtering
        # For demonstration, we'll show the filter summary
        filter_summary = engine.video_filter.get_filter_summary()
        
        print("\nActive Filters:")
        for filter_name, filter_value in filter_summary.items():
            if filter_value is not None and filter_value != False:
                print(f"  ✓ {filter_name}: {filter_value}")
        
        results = engine.search_videos(config.search_query)
        print(f"\nFinal Results: {len(results)} videos passed all filters")
        
    except Exception as e:
        print(f"Filter analysis failed: {e}")


def search_comparison_example():
    """Compare results with different search configurations."""
    print("=" * 60)
    print("SEARCH COMPARISON EXAMPLE")
    print("=" * 60)
    
    query = "web development tutorial"
    
    # Configuration 1: Broad search
    config1 = SearchConfig(
        search_query=query,
        max_results=10,
        sort_by="relevance"
    )
    
    # Configuration 2: Quality-focused search
    config2 = SearchConfig(
        search_query=query,
        max_results=10,
        sort_by="view_count",
        filter_config=FilterConfig(
            min_duration=600,     # At least 10 minutes
            min_view_count=50000,  # At least 50k views
            exclude_shorts=True,
            exclude_live=True
        )
    )
    
    try:
        print(f"Comparing search results for: '{query}'")
        print("\n1. BROAD SEARCH (Default filters)")
        print("-" * 40)
        
        engine1 = SearchEngine(config1)
        results1 = engine1.search_videos(query)
        print(f"Found: {len(results1)} videos")
        
        print("\n2. QUALITY-FOCUSED SEARCH (Strict filters)")
        print("-" * 40)
        
        engine2 = SearchEngine(config2)
        results2 = engine2.search_videos(query)
        print(f"Found: {len(results2)} videos")
        
        print(f"\nComparison:")
        print(f"  Broad search: {len(results1)} results")
        print(f"  Quality search: {len(results2)} results")
        print(f"  Filter efficiency: {(len(results2)/len(results1)*100):.1f}% retention" if results1 else "N/A")
        
    except Exception as e:
        print(f"Search comparison failed: {e}")


def main():
    """Run all examples."""
    setup_logging()
    
    print("YouTube Search Engine Examples")
    print("==============================")
    print("This script demonstrates the new batch search functionality.")
    print("Note: These examples use mock data when yt-dlp is not available.\n")
    
    try:
        # Run all examples
        basic_search_example()
        print("\n")
        
        advanced_filtering_example()
        print("\n")
        
        search_config_manager_example()
        print("\n")
        
        filter_analysis_example()
        print("\n")
        
        search_comparison_example()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.error(f"Unexpected error in main: {e}", exc_info=True)


if __name__ == "__main__":
    main() 