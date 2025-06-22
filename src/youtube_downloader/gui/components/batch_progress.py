"""
Batch Progress Panel Component

Displays progress information for batch YouTube downloads including
overall progress, individual video status, and download controls.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
import threading
from datetime import datetime
from enum import Enum

from ..styles.themes import theme_manager


class DownloadStatus(Enum):
    """Enum for download status."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class BatchDownloadItem:
    """Data class for batch download item."""
    
    def __init__(self, video_id: str, title: str, url: str):
        self.video_id = video_id
        self.title = title
        self.url = url
        self.status = DownloadStatus.PENDING
        self.progress = 0.0  # 0-100
        self.speed = ""
        self.eta = ""
        self.file_size = ""
        self.downloaded_size = ""
        self.error_message = ""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None


class BatchProgressPanel(ctk.CTkFrame):
    """
    Modern batch progress panel for YouTube download monitoring.
    
    Features:
    - Overall progress tracking
    - Individual video progress display
    - Download speed and ETA information
    - Pause/Resume/Cancel controls
    - Real-time log display
    - Download statistics
    """
    
    def __init__(self, parent, 
                 on_pause: Optional[Callable[[], None]] = None,
                 on_resume: Optional[Callable[[], None]] = None,
                 on_cancel: Optional[Callable[[], None]] = None):
        """
        Initialize batch progress panel.
        
        Args:
            parent: Parent widget
            on_pause: Callback for pause action
            on_resume: Callback for resume action
            on_cancel: Callback for cancel action
        """
        super().__init__(parent)
        
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_cancel = on_cancel
        
        # State variables
        self.download_items: List[BatchDownloadItem] = []
        self.is_downloading = False
        self.is_paused = False
        self.overall_progress = 0.0
        self.current_video_title = ""
        self.total_videos = 0
        self.completed_videos = 0
        self.failed_videos = 0
        self.start_time: Optional[datetime] = None
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Progress list should expand
        
        # Header section
        self._create_header()
        
        # Overall progress section
        self._create_overall_progress()
        
        # Controls section
        self._create_controls()
        
        # Individual progress list
        self._create_progress_list()
        
        # Statistics section
        self._create_statistics()
        
        # Initially hide the panel
        self._show_panel(False)
    
    def _create_header(self) -> None:
        """Create header section."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="📥 Batch Download Progress",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("accent")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Status badge
        self.status_badge = ctk.CTkLabel(
            header_frame,
            text="Ready",
            font=theme_manager.get_font("small"),
            text_color="white",
            fg_color=theme_manager.get_color("text_secondary"),
            corner_radius=12,
            width=60,
            height=24
        )
        self.status_badge.grid(row=0, column=1, sticky="e", padx=(0, 12))
    
    def _create_overall_progress(self) -> None:
        """Create overall progress section."""
        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        progress_frame.grid_columnconfigure(1, weight=1)
        
        # Current video label
        self.current_video_label = ctk.CTkLabel(
            progress_frame,
            text="No active downloads",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        self.current_video_label.grid(row=0, column=0, columnspan=2, sticky="w", 
                                     padx=12, pady=(12, 4))
        
        # Progress bar
        self.overall_progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            progress_color=theme_manager.get_color("accent")
        )
        self.overall_progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", 
                                      padx=12, pady=(0, 8))
        self.overall_progress_bar.set(0)
        
        # Progress text
        self.progress_text_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.progress_text_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 8))
        
        # Speed and ETA
        self.speed_eta_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.speed_eta_label.grid(row=2, column=1, sticky="e", padx=12, pady=(0, 8))
    
    def _create_controls(self) -> None:
        """Create control buttons section."""
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
        controls_frame.grid_columnconfigure(3, weight=1)  # Spacer column
        
        # Pause/Resume button
        self.pause_resume_btn = ctk.CTkButton(
            controls_frame,
            text="⏸️ Pause",
            width=100,
            height=32,
            font=theme_manager.get_font("body"),
            command=self._toggle_pause_resume,
            state="disabled"
        )
        self.pause_resume_btn.grid(row=0, column=0, padx=(12, 8), pady=8)
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            controls_frame,
            text="❌ Cancel",
            width=100,
            height=32,
            font=theme_manager.get_font("body"),
            command=self._cancel_download,
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.cancel_btn.grid(row=0, column=1, padx=8, pady=8)
        
        # Clear completed button
        self.clear_btn = ctk.CTkButton(
            controls_frame,
            text="🧹 Clear Completed",
            width=120,
            height=32,
            font=theme_manager.get_font("body"),
            command=self._clear_completed
        )
        self.clear_btn.grid(row=0, column=4, padx=(8, 12), pady=8)
    
    def _create_progress_list(self) -> None:
        """Create individual progress list."""
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 8))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview style
        style = ttk.Style()
        
        # Configure treeview colors
        style.configure("Progress.Treeview",
                       background=theme_manager.get_color("bg_secondary"),
                       foreground=theme_manager.get_color("text_primary"),
                       fieldbackground=theme_manager.get_color("bg_secondary"),
                       borderwidth=0,
                       font=theme_manager.get_font("small"))
        
        style.configure("Progress.Treeview.Heading",
                       background=theme_manager.get_color("accent"),
                       foreground="white",
                       font=theme_manager.get_font("body"))
        
        # Create treeview
        columns = ("status", "title", "progress", "speed", "eta", "size")
        
        self.progress_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            style="Progress.Treeview",
            height=8
        )
        
        # Configure columns
        self.progress_tree.heading("status", text="Status", anchor="center")
        self.progress_tree.heading("title", text="Video Title", anchor="w")
        self.progress_tree.heading("progress", text="Progress", anchor="center")
        self.progress_tree.heading("speed", text="Speed", anchor="center")
        self.progress_tree.heading("eta", text="ETA", anchor="center")
        self.progress_tree.heading("size", text="Size", anchor="center")
        
        # Configure column widths
        self.progress_tree.column("status", width=80, minwidth=80, anchor="center")
        self.progress_tree.column("title", width=300, minwidth=200, anchor="w")
        self.progress_tree.column("progress", width=100, minwidth=80, anchor="center")
        self.progress_tree.column("speed", width=100, minwidth=80, anchor="center")
        self.progress_tree.column("eta", width=80, minwidth=60, anchor="center")
        self.progress_tree.column("size", width=100, minwidth=80, anchor="center")
        
        self.progress_tree.grid(row=0, column=0, sticky="nsew")
        
        # Create scrollbar
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.progress_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.progress_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placeholder label
        self.progress_placeholder = ctk.CTkLabel(
            list_frame,
            text="📥 No downloads in progress\n\nStart a batch download to see progress here",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_secondary"),
            justify="center"
        )
        self.progress_placeholder.grid(row=0, column=0, sticky="nsew")
        
        # Initially show placeholder
        self._show_progress_placeholder(True)
    
    def _create_statistics(self) -> None:
        """Create statistics section."""
        stats_frame = ctk.CTkFrame(self, height=60)
        stats_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 12))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        stats_frame.grid_propagate(False)
        
        # Total videos
        self.total_stat = self._create_stat_widget(stats_frame, "Total", "0", 0)
        
        # Completed videos
        self.completed_stat = self._create_stat_widget(stats_frame, "Completed", "0", 1, 
                                                      color=theme_manager.get_color("success"))
        
        # Failed videos
        self.failed_stat = self._create_stat_widget(stats_frame, "Failed", "0", 2,
                                                   color="#dc3545")
        
        # Elapsed time
        self.time_stat = self._create_stat_widget(stats_frame, "Elapsed", "00:00", 3)
    
    def _create_stat_widget(self, parent, label: str, value: str, column: int, 
                           color: Optional[str] = None) -> ctk.CTkLabel:
        """Create a statistics widget."""
        stat_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stat_frame.grid(row=0, column=column, sticky="nsew", padx=8, pady=8)
        
        # Label
        label_widget = ctk.CTkLabel(
            stat_frame,
            text=label,
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        label_widget.pack(pady=(8, 2))
        
        # Value
        value_widget = ctk.CTkLabel(
            stat_frame,
            text=value,
            font=theme_manager.get_font("heading"),
            text_color=color or theme_manager.get_color("text_primary")
        )
        value_widget.pack(pady=(0, 8))
        
        return value_widget
    
    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        # Double-click to show error details
        self.progress_tree.bind("<Double-1>", self._show_item_details)
    
    def _show_panel(self, show: bool) -> None:
        """Show or hide the entire panel."""
        if show:
            self.grid()
        else:
            self.grid_remove()
    
    def _show_progress_placeholder(self, show: bool) -> None:
        """Show or hide progress placeholder."""
        if show:
            self.progress_tree.grid_remove()
            self.progress_placeholder.grid(row=0, column=0, sticky="nsew")
        else:
            self.progress_placeholder.grid_remove()
            self.progress_tree.grid(row=0, column=0, sticky="nsew")
    
    def _toggle_pause_resume(self) -> None:
        """Toggle between pause and resume."""
        if self.is_paused:
            self._resume_download()
        else:
            self._pause_download()
    
    def _pause_download(self) -> None:
        """Pause download."""
        if self.on_pause:
            self.on_pause()
        self.is_paused = True
        self.pause_resume_btn.configure(text="▶️ Resume")
        self.status_badge.configure(text="Paused", fg_color="#ffc107")
    
    def _resume_download(self) -> None:
        """Resume download."""
        if self.on_resume:
            self.on_resume()
        self.is_paused = False
        self.pause_resume_btn.configure(text="⏸️ Pause")
        self.status_badge.configure(text="Downloading", fg_color=theme_manager.get_color("accent"))
    
    def _cancel_download(self) -> None:
        """Cancel download."""
        if self.on_cancel:
            self.on_cancel()
        self.is_downloading = False
        self.is_paused = False
        self.pause_resume_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        self.status_badge.configure(text="Cancelled", fg_color="#dc3545")
    
    def _clear_completed(self) -> None:
        """Clear completed downloads from the list."""
        self.download_items = [item for item in self.download_items 
                              if item.status not in [DownloadStatus.COMPLETED, DownloadStatus.FAILED]]
        self._refresh_progress_list()
        self._update_statistics()
    
    def _show_item_details(self, event) -> None:
        """Show details for selected item."""
        selection = self.progress_tree.selection()
        if selection:
            item_id = selection[0]
            try:
                item_index = int(item_id) - 1
                if 0 <= item_index < len(self.download_items):
                    item = self.download_items[item_index]
                    if item.error_message:
                        tk.messagebox.showerror("Download Error", 
                                              f"Video: {item.title}\n\nError: {item.error_message}")
            except (ValueError, IndexError):
                pass
    
    def _refresh_progress_list(self) -> None:
        """Refresh the progress list display."""
        # Clear existing items
        for item in self.progress_tree.get_children():
            self.progress_tree.delete(item)
        
        # Add current items
        for i, item in enumerate(self.download_items, 1):
            status_text = self._get_status_text(item.status)
            progress_text = f"{item.progress:.1f}%" if item.progress > 0 else "0%"
            
            # Truncate title if too long
            title_text = item.title[:50] + "..." if len(item.title) > 50 else item.title
            
            self.progress_tree.insert("", "end", iid=str(i), values=(
                status_text,
                title_text,
                progress_text,
                item.speed,
                item.eta,
                item.file_size
            ))
        
        # Show/hide placeholder
        self._show_progress_placeholder(len(self.download_items) == 0)
    
    def _get_status_text(self, status: DownloadStatus) -> str:
        """Get display text for status."""
        status_map = {
            DownloadStatus.PENDING: "⏳ Pending",
            DownloadStatus.DOWNLOADING: "⬇️ Downloading",
            DownloadStatus.COMPLETED: "✅ Completed",
            DownloadStatus.FAILED: "❌ Failed",
            DownloadStatus.CANCELLED: "🚫 Cancelled",
            DownloadStatus.PAUSED: "⏸️ Paused"
        }
        return status_map.get(status, "❓ Unknown")
    
    def _update_statistics(self) -> None:
        """Update statistics display."""
        self.total_stat.configure(text=str(self.total_videos))
        self.completed_stat.configure(text=str(self.completed_videos))
        self.failed_stat.configure(text=str(self.failed_videos))
        
        # Update elapsed time
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.time_stat.configure(text=time_str)
    
    def start_batch_download(self, video_items: List[Dict[str, Any]]) -> None:
        """Start a new batch download."""
        # Initialize download items
        self.download_items = []
        for item_data in video_items:
            download_item = BatchDownloadItem(
                video_id=item_data.get('video_id', ''),
                title=item_data.get('title', 'Unknown Title'),
                url=item_data.get('url', '')
            )
            self.download_items.append(download_item)
        
        # Reset state
        self.is_downloading = True
        self.is_paused = False
        self.overall_progress = 0.0
        self.total_videos = len(self.download_items)
        self.completed_videos = 0
        self.failed_videos = 0
        self.start_time = datetime.now()
        
        # Update UI
        self._show_panel(True)
        self.pause_resume_btn.configure(state="normal", text="⏸️ Pause")
        self.cancel_btn.configure(state="normal")
        self.status_badge.configure(text="Downloading", fg_color=theme_manager.get_color("accent"))
        self.current_video_label.configure(text="Preparing downloads...")
        
        self._refresh_progress_list()
        self._update_statistics()
    
    def update_progress(self, video_id: str, progress_data: Dict[str, Any]) -> None:
        """Update progress for a specific video."""
        # Find the download item
        item = next((item for item in self.download_items if item.video_id == video_id), None)
        if not item:
            return
        
        # Update item data
        item.progress = progress_data.get('progress', 0.0)
        item.speed = progress_data.get('speed', '')
        item.eta = progress_data.get('eta', '')
        item.file_size = progress_data.get('total_size', '')
        item.downloaded_size = progress_data.get('downloaded_size', '')
        
        # Update status
        if progress_data.get('status') == 'downloading':
            item.status = DownloadStatus.DOWNLOADING
            if not item.start_time:
                item.start_time = datetime.now()
        elif progress_data.get('status') == 'completed':
            item.status = DownloadStatus.COMPLETED
            item.end_time = datetime.now()
            self.completed_videos += 1
        elif progress_data.get('status') == 'failed':
            item.status = DownloadStatus.FAILED
            item.error_message = progress_data.get('error', 'Unknown error')
            self.failed_videos += 1
        
        # Update current video display
        if item.status == DownloadStatus.DOWNLOADING:
            self.current_video_label.configure(text=f"Downloading: {item.title}")
        
        # Update overall progress
        total_progress = sum(item.progress for item in self.download_items)
        self.overall_progress = total_progress / len(self.download_items) if self.download_items else 0
        self.overall_progress_bar.set(self.overall_progress / 100)
        
        # Update progress text
        self.progress_text_label.configure(text=f"{self.overall_progress:.1f}%")
        
        # Update speed and ETA (use current downloading item)
        downloading_items = [item for item in self.download_items 
                           if item.status == DownloadStatus.DOWNLOADING]
        if downloading_items:
            current_item = downloading_items[0]
            speed_eta_text = f"{current_item.speed}"
            if current_item.eta:
                speed_eta_text += f" • ETA: {current_item.eta}"
            self.speed_eta_label.configure(text=speed_eta_text)
        
        # Refresh display
        self._refresh_progress_list()
        self._update_statistics()
        
        # Check if all downloads are complete
        if all(item.status in [DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED] 
               for item in self.download_items):
            self._on_batch_complete()
    
    def _on_batch_complete(self) -> None:
        """Handle batch download completion."""
        self.is_downloading = False
        self.is_paused = False
        self.pause_resume_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        
        # Update status
        if self.failed_videos > 0:
            self.status_badge.configure(text="Completed with errors", fg_color="#ffc107")
        else:
            self.status_badge.configure(text="Completed", fg_color=theme_manager.get_color("success"))
        
        self.current_video_label.configure(text="Batch download completed")
        self.speed_eta_label.configure(text="")
    
    def reset(self) -> None:
        """Reset the progress panel."""
        self.download_items.clear()
        self.is_downloading = False
        self.is_paused = False
        self.overall_progress = 0.0
        self.completed_videos = 0
        self.failed_videos = 0
        self.total_videos = 0
        self.start_time = None
        
        # Reset UI
        self.overall_progress_bar.set(0)
        self.progress_text_label.configure(text="0%")
        self.speed_eta_label.configure(text="")
        self.current_video_label.configure(text="No active downloads")
        self.status_badge.configure(text="Ready", fg_color=theme_manager.get_color("text_secondary"))
        self.pause_resume_btn.configure(state="disabled", text="⏸️ Pause")
        self.cancel_btn.configure(state="disabled")
        
        self._refresh_progress_list()
        self._update_statistics()
        self._show_panel(False)
    
    def get_download_summary(self) -> Dict[str, Any]:
        """Get download summary statistics."""
        return {
            'total_videos': self.total_videos,
            'completed_videos': self.completed_videos,
            'failed_videos': self.failed_videos,
            'is_downloading': self.is_downloading,
            'is_paused': self.is_paused,
            'overall_progress': self.overall_progress,
            'start_time': self.start_time,
            'failed_items': [item for item in self.download_items if item.status == DownloadStatus.FAILED]
        } 