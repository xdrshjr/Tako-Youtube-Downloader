"""
Progress Panel Component

Displays download progress with modern progress bars, status information,
and estimated time remaining. Provides clear visual feedback to users.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
import time

from ..styles.themes import theme_manager


class ProgressPanel(ctk.CTkFrame):
    """
    Modern progress display panel with visual feedback.
    
    Features:
    - Animated progress bar
    - Download speed indicator
    - ETA calculation
    - Status messages
    - File size information
    """
    
    def __init__(self, parent):
        """Initialize progress panel."""
        super().__init__(parent)
        
        self.start_time = None
        self.bytes_downloaded = 0
        self.total_bytes = 0
        self.current_status = "idle"
        
        self._setup_ui()
        self.reset()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.grid_columnconfigure(1, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Download Progress",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("text_primary")
        )
        self.title_label.grid(
            row=0, column=0, columnspan=2,
            sticky="w", padx=16, pady=(16, 8)
        )
        
        # Progress frame
        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(
            row=1, column=0, columnspan=2,
            sticky="ew", padx=16, pady=(0, 8)
        )
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            corner_radius=10
        )
        self.progress_bar.grid(
            row=0, column=0,
            sticky="ew", padx=16, pady=(16, 8)
        )
        self.progress_bar.set(0)
        
        # Progress percentage
        self.percentage_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        self.percentage_label.grid(
            row=0, column=1,
            padx=(8, 16), pady=(16, 8)
        )
        
        # Status information frame
        status_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        status_frame.grid(
            row=1, column=0, columnspan=2,
            sticky="ew", padx=16, pady=(0, 16)
        )
        status_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to download",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.status_label.grid(
            row=0, column=0, columnspan=3,
            sticky="w", pady=(0, 4)
        )
        
        # Download speed
        self.speed_label = ctk.CTkLabel(
            status_frame,
            text="Speed: --",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.speed_label.grid(
            row=1, column=0,
            sticky="w"
        )
        
        # Downloaded/Total size
        self.size_label = ctk.CTkLabel(
            status_frame,
            text="Size: --",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.size_label.grid(
            row=1, column=1,
            sticky="w"
        )
        
        # ETA
        self.eta_label = ctk.CTkLabel(
            status_frame,
            text="ETA: --",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.eta_label.grid(
            row=1, column=2,
            sticky="w"
        )
    
    def update_progress(self, progress_data: Dict[str, Any]) -> None:
        """
        Update progress display with new data.
        
        Args:
            progress_data: Dictionary containing progress information
        """
        status = progress_data.get('status', 'unknown')
        
        if status == 'downloading':
            self._update_downloading(progress_data)
        elif status == 'finished':
            self._update_finished(progress_data)
        elif status == 'error':
            self._update_error(progress_data)
        else:
            self._update_status(f"Status: {status}")
    
    def _update_downloading(self, data: Dict[str, Any]) -> None:
        """Update display during download."""
        if self.start_time is None:
            self.start_time = time.time()
        
        # Update progress bar
        if 'total_bytes' in data and data['total_bytes']:
            self.total_bytes = data['total_bytes']
            self.bytes_downloaded = data.get('downloaded_bytes', 0)
            progress = self.bytes_downloaded / self.total_bytes
            self.progress_bar.set(progress)
            self.percentage_label.configure(text=f"{progress * 100:.1f}%")
        elif '_percent_str' in data:
            # Fallback to yt-dlp's percentage string
            percent_str = data['_percent_str'].strip()
            self.percentage_label.configure(text=percent_str)
            try:
                percent_value = float(percent_str.replace('%', '')) / 100
                self.progress_bar.set(percent_value)
            except ValueError:
                pass
        
        # Update speed
        speed = data.get('speed')
        if speed:
            speed_str = self._format_speed(speed)
            self.speed_label.configure(text=f"Speed: {speed_str}")
        
        # Update size information
        if self.total_bytes > 0:
            size_str = f"{self._format_bytes(self.bytes_downloaded)} / {self._format_bytes(self.total_bytes)}"
            self.size_label.configure(text=f"Size: {size_str}")
        
        # Update ETA
        if self.bytes_downloaded > 0 and self.total_bytes > 0 and speed:
            remaining_bytes = self.total_bytes - self.bytes_downloaded
            eta_seconds = remaining_bytes / speed
            eta_str = self._format_time(eta_seconds)
            self.eta_label.configure(text=f"ETA: {eta_str}")
        
        # Update status
        filename = data.get('filename', '')
        if filename:
            self._update_status(f"Downloading: {filename}")
        else:
            self._update_status("Downloading...")
    
    def _update_finished(self, data: Dict[str, Any]) -> None:
        """Update display when download is finished."""
        self.progress_bar.set(1.0)
        self.percentage_label.configure(text="100%")
        
        filename = data.get('filename', 'file')
        self._update_status(f"✓ Download completed: {filename}", "success")
        
        # Calculate total time
        if self.start_time:
            total_time = time.time() - self.start_time
            time_str = self._format_time(total_time)
            self.eta_label.configure(text=f"Completed in: {time_str}")
    
    def _update_error(self, data: Dict[str, Any]) -> None:
        """Update display when an error occurs."""
        error_message = data.get('error', 'Unknown error')
        self._update_status(f"✗ Error: {error_message}", "error")
    
    def _update_status(self, message: str, status_type: str = "info") -> None:
        """Update status message with appropriate styling."""
        self.current_status = status_type
        
        # Set color based on status type
        color_map = {
            "info": theme_manager.get_color("text_secondary"),
            "success": theme_manager.get_color("success"),
            "warning": theme_manager.get_color("warning"),
            "error": theme_manager.get_color("error")
        }
        
        color = color_map.get(status_type, theme_manager.get_color("text_secondary"))
        self.status_label.configure(text=message, text_color=color)
    
    def set_preparing(self, message: str = "Preparing download...") -> None:
        """Set preparing state."""
        self._update_status(message, "info")
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
    
    def set_fetching_info(self, message: str = "Fetching video information...") -> None:
        """Set info fetching state."""
        self._update_status(message, "info")
        # Use indeterminate progress
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.percentage_label.configure(text="...")
    
    def set_ready(self, message: str = "Ready to download") -> None:
        """Set ready state."""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self._update_status(message, "info")
        self.reset()
    
    def reset(self) -> None:
        """Reset progress display to initial state."""
        self.start_time = None
        self.bytes_downloaded = 0
        self.total_bytes = 0
        self.current_status = "idle"
        
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        self.speed_label.configure(text="Speed: --")
        self.size_label.configure(text="Size: --")
        self.eta_label.configure(text="ETA: --")
        self._update_status("Ready to download")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"
    
    def _format_speed(self, speed: float) -> str:
        """Format download speed into human-readable string."""
        return f"{self._format_bytes(speed)}/s"
    
    def _format_time(self, seconds: float) -> str:
        """Format time into human-readable string."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m" 