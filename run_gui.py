#!/usr/bin/env python3
"""
Quick start script for YouTube Downloader GUI

This is a convenience script that launches the GUI application.
Simply double-click this file or run it from the command line.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def main():
    """Launch the GUI application."""
    try:
        # Import and run the GUI
        from youtube_downloader.gui_main import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 Make sure you've installed the required dependencies:")
        print("   pip install -r requirements.txt")
        print("\n📂 And that you're running this script from the project root directory.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main() 