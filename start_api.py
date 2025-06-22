#!/usr/bin/env python3
"""
YouTube Downloader API Startup Script

This script provides a convenient way to start the FastAPI server for the
YouTube Downloader project.

Usage:
    python start_api.py [options]

Options:
    --host HOST        Host to bind to (default: 0.0.0.0)
    --port PORT        Port to bind to (default: 8000)
    --reload           Enable auto-reload for development (default: False)
    --workers WORKERS  Number of worker processes (default: 1)
    --log-level LEVEL  Log level (debug, info, warning, error, critical) (default: info)
    --dev              Development mode (enables reload and debug logging)
    --help             Show this help message
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import uvicorn
    from youtube_downloader.api.main import app
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def setup_logging(level: str = "info"):
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('api.log')
        ]
    )


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'yt_dlp'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required dependencies:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install them using:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def create_directories():
    """Create necessary directories."""
    directories = [
        './downloads',
        './logs',
        './config'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def main():
    """Main function to start the API server."""
    parser = argparse.ArgumentParser(
        description="YouTube Downloader API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind to (default: 8000)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='info',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Log level (default: info)'
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Development mode (enables reload and debug logging)'
    )
    
    args = parser.parse_args()
    
    # Development mode overrides
    if args.dev:
        args.reload = True
        args.log_level = 'debug'
        print("🔧 Development mode enabled")
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    print("🎬 YouTube Downloader API")
    print("=" * 40)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies are installed")
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Display configuration
    print(f"\n⚙️ Configuration:")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Workers: {args.workers}")
    print(f"   Reload: {args.reload}")
    print(f"   Log Level: {args.log_level.upper()}")
    
    # Display endpoints
    print(f"\n🌐 API Endpoints:")
    print(f"   Health Check: http://{args.host}:{args.port}/health")
    print(f"   API Docs: http://{args.host}:{args.port}/docs")
    print(f"   ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"   API Info: http://{args.host}:{args.port}/api/v1/info")
    
    print(f"\n🚀 Starting API server...")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the server
        uvicorn.run(
            "youtube_downloader.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,  # Workers=1 when reload is enabled
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        print("\n👋 Server stopped gracefully")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 