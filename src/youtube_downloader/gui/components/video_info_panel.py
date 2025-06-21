"""
Video Info Panel Component

Displays YouTube video information in an elegant, organized layout.
Shows title, uploader, duration, views, and other metadata.
"""

import customtkinter as ctk
from typing import Optional
from datetime import datetime

from ..styles.themes import theme_manager


class VideoInfoPanel(ctk.CTkFrame):
    """
    Modern video information display panel.
    
    Features:
    - Video title and description
    - Channel information
    - Video statistics (views, likes, duration)
    - Upload date
    - Thumbnail placeholder
    - Clean, organized layout
    """
    
    def __init__(self, parent):
        """Initialize video info panel."""
        super().__init__(parent)
        
        self.video_info = None
        self._setup_ui()
        self.clear_info()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.grid_columnconfigure(1, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Video Information",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("text_primary")
        )
        self.title_label.grid(
            row=0, column=0, columnspan=2,
            sticky="w", padx=16, pady=(16, 8)
        )
        
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(
            row=1, column=0, columnspan=2,
            sticky="ew", padx=16, pady=(0, 16)
        )
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Thumbnail placeholder (left side)
        self.thumbnail_frame = ctk.CTkFrame(content_frame, width=120, height=90)
        self.thumbnail_frame.grid(
            row=0, column=0, rowspan=4,
            padx=16, pady=16, sticky="nw"
        )
        self.thumbnail_frame.grid_propagate(False)
        
        self.thumbnail_label = ctk.CTkLabel(
            self.thumbnail_frame,
            text="📹\nThumbnail",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_disabled"),
            justify="center"
        )
        self.thumbnail_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Video details (right side)
        details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        details_frame.grid(
            row=0, column=1,
            sticky="ew", padx=(16, 16), pady=16
        )
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Video title
        self.video_title = ctk.CTkLabel(
            details_frame,
            text="No video selected",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("text_primary"),
            wraplength=400,
            justify="left"
        )
        self.video_title.grid(
            row=0, column=0,
            sticky="ew", pady=(0, 8)
        )
        
        # Channel name
        self.channel_label = ctk.CTkLabel(
            details_frame,
            text="Channel: --",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.channel_label.grid(
            row=1, column=0,
            sticky="w", pady=(0, 4)
        )
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        stats_frame.grid(
            row=2, column=0,
            sticky="ew", pady=(8, 0)
        )
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Duration
        self.duration_label = ctk.CTkLabel(
            stats_frame,
            text="Duration: --",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.duration_label.grid(
            row=0, column=0,
            sticky="w"
        )
        
        # Views
        self.views_label = ctk.CTkLabel(
            stats_frame,
            text="Views: --",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.views_label.grid(
            row=0, column=1,
            sticky="w"
        )
        
        # Upload date
        self.upload_date_label = ctk.CTkLabel(
            stats_frame,
            text="Uploaded: --",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.upload_date_label.grid(
            row=0, column=2,
            sticky="w"
        )
        
        # Likes (if available)
        self.likes_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.likes_label.grid(
            row=1, column=0,
            sticky="w", pady=(4, 0)
        )
        
        # Video ID
        self.video_id_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_disabled")
        )
        self.video_id_label.grid(
            row=1, column=1, columnspan=2,
            sticky="w", pady=(4, 0)
        )
    
    def set_video_info(self, video_info) -> None:
        """
        Update display with video information.
        
        Args:
            video_info: VideoInfo object with video metadata
        """
        self.video_info = video_info
        
        # Update video title
        title = video_info.title or "Unknown Title"
        # Truncate very long titles
        if len(title) > 80:
            title = title[:77] + "..."
        self.video_title.configure(text=title)
        
        # Update channel
        channel = video_info.uploader or "Unknown Channel"
        self.channel_label.configure(text=f"Channel: {channel}")
        
        # Update duration
        duration_str = self._format_duration(video_info.duration)
        self.duration_label.configure(text=f"Duration: {duration_str}")
        
        # Update views
        views_str = self._format_number(video_info.view_count)
        self.views_label.configure(text=f"Views: {views_str}")
        
        # Update upload date
        upload_date_str = self._format_upload_date(video_info.upload_date)
        self.upload_date_label.configure(text=f"Uploaded: {upload_date_str}")
        
        # Update likes (if available)
        if video_info.like_count:
            likes_str = self._format_number(video_info.like_count)
            self.likes_label.configure(text=f"👍 {likes_str} likes")
        else:
            self.likes_label.configure(text="")
        
        # Update video ID
        video_id = getattr(video_info, 'id', None) or "Unknown ID"
        self.video_id_label.configure(text=f"ID: {video_id}")
        
        # Update thumbnail placeholder
        self.thumbnail_label.configure(text="📹\nLoaded")
    
    def clear_info(self) -> None:
        """Clear video information display."""
        self.video_info = None
        
        self.video_title.configure(text="No video selected")
        self.channel_label.configure(text="Channel: --")
        self.duration_label.configure(text="Duration: --")
        self.views_label.configure(text="Views: --")
        self.upload_date_label.configure(text="Uploaded: --")
        self.likes_label.configure(text="")
        self.video_id_label.configure(text="")
        self.thumbnail_label.configure(text="📹\nThumbnail")
    
    def set_loading(self) -> None:
        """Set loading state."""
        self.video_title.configure(text="Loading video information...")
        self.channel_label.configure(text="Channel: ...")
        self.duration_label.configure(text="Duration: ...")
        self.views_label.configure(text="Views: ...")
        self.upload_date_label.configure(text="Uploaded: ...")
        self.likes_label.configure(text="")
        self.video_id_label.configure(text="")
        self.thumbnail_label.configure(text="📹\nLoading...")
    
    def set_error(self, error_message: str = "Failed to load video information") -> None:
        """Set error state."""
        self.video_title.configure(
            text=error_message,
            text_color=theme_manager.get_color("error")
        )
        self.channel_label.configure(text="Channel: --")
        self.duration_label.configure(text="Duration: --")
        self.views_label.configure(text="Views: --")
        self.upload_date_label.configure(text="Uploaded: --")
        self.likes_label.configure(text="")
        self.video_id_label.configure(text="")
        self.thumbnail_label.configure(text="📹\nError")
    
    def _format_duration(self, seconds: Optional[int]) -> str:
        """Format duration from seconds to readable string."""
        if not seconds:
            return "--"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def _format_number(self, number: Optional[int]) -> str:
        """Format large numbers with appropriate suffixes."""
        if not number:
            return "--"
        
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.1f}B"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}K"
        else:
            return f"{number:,}"
    
    def _format_upload_date(self, upload_date: Optional[str]) -> str:
        """Format upload date string."""
        if not upload_date:
            return "--"
        
        try:
            # Parse YYYYMMDD format
            if len(upload_date) == 8 and upload_date.isdigit():
                year = int(upload_date[:4])
                month = int(upload_date[4:6])
                day = int(upload_date[6:8])
                date_obj = datetime(year, month, day)
                return date_obj.strftime("%B %d, %Y")
            else:
                return upload_date
        except (ValueError, TypeError):
            return upload_date or "--" 