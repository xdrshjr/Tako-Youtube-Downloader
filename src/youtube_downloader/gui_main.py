#!/usr/bin/env python3
"""
YouTube Downloader GUI Application - Main Entry Point

This is the main entry point for the desktop GUI application.
It provides a modern, elegant interface for downloading YouTube videos.

Usage:
    python -m src.youtube_downloader.gui_main
    
Features:
    - Modern CustomTkinter-based GUI
    - Real-time download progress
    - Video information display
    - Settings management
    - Comprehensive logging
    - Dark/Light theme support
"""

import sys
import os
import logging
from pathlib import Path

# Add the source directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Configure logging for GUI
def setup_gui_logging():
    """Set up logging configuration for the GUI application."""
    log_dir = Path.home() / "Downloads" / "YouTube" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "youtube_downloader_gui.log"
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Create handlers
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()  # Clear any existing handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('youtube_downloader').setLevel(logging.DEBUG)
    logging.getLogger('yt_dlp').setLevel(logging.WARNING)  # Reduce yt-dlp verbosity
    
    return log_file


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = {
        'customtkinter': 'customtkinter>=5.2.0',
        'PIL': 'pillow>=10.0.0',
        'yt_dlp': 'yt-dlp>=2024.1.1',
        'yaml': 'pyyaml>=6.0.0',
        'requests': 'requests>=2.28.0'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("❌ Missing required dependencies:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing dependencies with:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("\nOr install all GUI dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main entry point for the GUI application."""
    print("🐙 TakoAI - YouTube Downloader")
    print("🎬 Professional Media Solutions - Phase 3 GUI")
    print("=" * 50)
    
    # Check dependencies first
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found")
    
    # Set up logging
    print("📝 Setting up logging...")
    log_file = setup_gui_logging()
    print(f"📁 Logs will be saved to: {log_file}")
    
    # Initialize logger for this module
    logger = logging.getLogger(__name__)
    logger.info("YouTube Downloader GUI starting...")
    
    try:
        # Import and configure CustomTkinter
        import customtkinter as ctk
        
        # Set default appearance
        ctk.set_appearance_mode("dark")  # Default to dark theme
        ctk.set_default_color_theme("blue")  # Default color theme
        
        logger.info("CustomTkinter configured successfully")
        
        # Import the main application
        try:
            from youtube_downloader.gui.main_window import YouTubeDownloaderApp
            logger.info("GUI components imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import GUI components: {e}")
            print(f"❌ Failed to import GUI components: {e}")
            print("Make sure you're running from the correct directory.")
            sys.exit(1)
        
        # Create and run the application
        print("🚀 Starting GUI application...")
        logger.info("Creating main application window")
        
        try:
            app = YouTubeDownloaderApp()
            
            # Log startup completion
            logger.info("GUI application initialized successfully")
            print("✅ GUI application started successfully!")
            print("💡 Press Ctrl+C in terminal to force quit if needed")
            print("📱 Use Ctrl+Q in the application to quit normally")
            
            # Start the main event loop
            app.mainloop()
            
        except Exception as e:
            logger.error(f"Error running GUI application: {e}", exc_info=True)
            print(f"❌ Error running application: {e}")
            raise
        
    except ImportError as e:
        logger.error(f"Failed to import CustomTkinter: {e}")
        print(f"❌ Failed to import CustomTkinter: {e}")
        print("Please install customtkinter: pip install customtkinter>=5.2.0")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n👋 Application interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}")
        print(f"📄 Check the log file for details: {log_file}")
        sys.exit(1)
    
    finally:
        logger.info("YouTube Downloader GUI shutting down")
        print("👋 YouTube Downloader GUI closed")


if __name__ == "__main__":
    main() 