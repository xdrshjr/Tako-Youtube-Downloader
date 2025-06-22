"""
Result List Component

Displays YouTube search results in a table format with selection controls
and batch operation capabilities for the YouTube downloader.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional, Set
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser

from ..styles.themes import theme_manager


class VideoResultItem:
    """Data class for video search result item."""
    
    def __init__(self, data: Dict[str, Any]):
        self.video_id: str = data.get('video_id', '')
        self.title: str = data.get('title', 'Unknown Title')
        self.duration: int = data.get('duration', 0)
        self.uploader: str = data.get('uploader', 'Unknown')
        self.upload_date: str = data.get('upload_date', '')
        self.view_count: int = data.get('view_count', 0)
        self.thumbnail_url: str = data.get('thumbnail_url', '')
        self.url: str = data.get('url', f'https://www.youtube.com/watch?v={self.video_id}')
        self.selected: bool = False
        self.thumbnail_image: Optional[ImageTk.PhotoImage] = None


class ResultList(ctk.CTkFrame):
    """
    Modern result list for YouTube search results display.
    
    Features:
    - Table display with sortable columns
    - Thumbnail previews
    - Selection checkboxes
    - Batch operations (select all/none/invert)
    - Video preview on click
    - Download selected videos functionality
    """
    
    def __init__(self, parent, on_download_selected: Optional[Callable[[List[VideoResultItem]], None]] = None):
        """
        Initialize result list.
        
        Args:
            parent: Parent widget
            on_download_selected: Callback function called when download is requested
        """
        super().__init__(parent)
        
        self.on_download_selected = on_download_selected
        self.results: List[VideoResultItem] = []
        self.selected_items: Set[str] = set()  # video_ids
        self.thumbnail_cache: Dict[str, ImageTk.PhotoImage] = {}
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Results table should expand
        
        # Header section
        self._create_header()
        
        # Status bar (create before controls so selection_label exists)
        self._create_status_bar()
        
        # Control buttons section
        self._create_controls()
        
        # Results table section
        self._create_results_table()
    
    def _create_header(self) -> None:
        """Create header section."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📺 Search Results",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("accent")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Results count
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="No results",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.count_label.grid(row=0, column=1, sticky="e")
    
    def _create_controls(self) -> None:
        """Create control buttons section."""
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        controls_frame.grid_columnconfigure(4, weight=1)  # Spacer column
        
        # Selection buttons
        self.select_all_btn = ctk.CTkButton(
            controls_frame,
            text="✅ Select All",
            width=100,
            height=28,
            font=theme_manager.get_font("small"),
            command=self._select_all
        )
        self.select_all_btn.grid(row=0, column=0, padx=(12, 4), pady=8)
        
        self.select_none_btn = ctk.CTkButton(
            controls_frame,
            text="❌ Select None",
            width=100,
            height=28,
            font=theme_manager.get_font("small"),
            command=self._select_none
        )
        self.select_none_btn.grid(row=0, column=1, padx=4, pady=8)
        
        self.invert_selection_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Invert",
            width=80,
            height=28,
            font=theme_manager.get_font("small"),
            command=self._invert_selection
        )
        self.invert_selection_btn.grid(row=0, column=2, padx=4, pady=8)
        
        # Download button
        self.download_selected_btn = ctk.CTkButton(
            controls_frame,
            text="⬇️ Download Selected",
            height=28,
            font=theme_manager.get_font("body"),
            command=self._download_selected,
            fg_color=theme_manager.get_color("accent"),
            hover_color=theme_manager.get_color("primary_hover"),
            state="disabled"
        )
        self.download_selected_btn.grid(row=0, column=5, padx=(4, 12), pady=8)
        
        # Initially disable controls
        self._update_controls_state()
    
    def _create_results_table(self) -> None:
        """Create results table with scrollbar."""
        # Create frame for table and scrollbar
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview style
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure treeview colors to match CustomTkinter theme
        style.configure("Custom.Treeview",
                       background=theme_manager.get_color("bg_secondary"),
                       foreground=theme_manager.get_color("text_primary"),
                       fieldbackground=theme_manager.get_color("bg_secondary"),
                       borderwidth=0,
                       font=theme_manager.get_font("small"))
        
        style.configure("Custom.Treeview.Heading",
                       background=theme_manager.get_color("accent"),
                       foreground="white",
                       font=theme_manager.get_font("body"),
                       borderwidth=1,
                       relief="solid")
        
        # Create treeview
        columns = ("select", "thumbnail", "title", "duration", "uploader", "views", "date")
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            height=12
        )
        
        # Configure columns
        self.tree.heading("select", text="☐", anchor="center")
        self.tree.heading("thumbnail", text="🖼️", anchor="center")
        self.tree.heading("title", text="Title", anchor="w")
        self.tree.heading("duration", text="Duration", anchor="center")
        self.tree.heading("uploader", text="Channel", anchor="w")
        self.tree.heading("views", text="Views", anchor="center")
        self.tree.heading("date", text="Upload Date", anchor="center")
        
        # Configure column widths
        self.tree.column("select", width=40, minwidth=40, anchor="center")
        self.tree.column("thumbnail", width=80, minwidth=80, anchor="center")
        self.tree.column("title", width=300, minwidth=200, anchor="w")
        self.tree.column("duration", width=80, minwidth=80, anchor="center")
        self.tree.column("uploader", width=150, minwidth=100, anchor="w")
        self.tree.column("views", width=100, minwidth=80, anchor="center")
        self.tree.column("date", width=100, minwidth=80, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Create scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Create placeholder label
        self.placeholder_label = ctk.CTkLabel(
            table_frame,
            text="🔍 No search results to display\n\nUse the search panel to find YouTube videos",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_secondary"),
            justify="center"
        )
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")
        
        # Initially show placeholder
        self._show_placeholder(True)
    
    def _create_status_bar(self) -> None:
        """Create status bar."""
        self.status_frame = ctk.CTkFrame(self, height=30)
        self.status_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.status_frame.grid_columnconfigure(1, weight=1)
        self.status_frame.grid_propagate(False)
        
        # Selection status
        self.selection_label = ctk.CTkLabel(
            self.status_frame,
            text="0 selected",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.selection_label.grid(row=0, column=0, sticky="w", padx=12, pady=6)
        
        # Loading status
        self.loading_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("accent")
        )
        self.loading_label.grid(row=0, column=1, sticky="e", padx=12, pady=6)
    
    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        # Double-click to open video
        self.tree.bind("<Double-1>", self._on_item_double_click)
        
        # Single-click on select column
        self.tree.bind("<Button-1>", self._on_item_click)
        
        # Right-click context menu
        self.tree.bind("<Button-3>", self._show_context_menu)
    
    def _show_placeholder(self, show: bool) -> None:
        """Show or hide placeholder text."""
        if show:
            self.tree.grid_remove()
            self.placeholder_label.grid(row=0, column=0, sticky="nsew")
        else:
            self.placeholder_label.grid_remove()
            self.tree.grid(row=0, column=0, sticky="nsew")
    
    def _select_all(self) -> None:
        """Select all items."""
        for result in self.results:
            result.selected = True
            self.selected_items.add(result.video_id)
        self._refresh_table()
        self._update_controls_state()
    
    def _select_none(self) -> None:
        """Deselect all items."""
        for result in self.results:
            result.selected = False
        self.selected_items.clear()
        self._refresh_table()
        self._update_controls_state()
    
    def _invert_selection(self) -> None:
        """Invert current selection."""
        for result in self.results:
            result.selected = not result.selected
            if result.selected:
                self.selected_items.add(result.video_id)
            else:
                self.selected_items.discard(result.video_id)
        self._refresh_table()
        self._update_controls_state()
    
    def _download_selected(self) -> None:
        """Download selected videos."""
        selected_results = [r for r in self.results if r.selected]
        if selected_results and self.on_download_selected:
            self.on_download_selected(selected_results)
    
    def _on_item_click(self, event) -> None:
        """Handle item click."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x, event.y)
            item_id = self.tree.identify_row(event.y)
            
            if column == "#1" and item_id:  # Select column
                self._toggle_item_selection(item_id)
    
    def _on_item_double_click(self, event) -> None:
        """Handle item double-click to open video."""
        item_id = self.tree.selection()[0] if self.tree.selection() else None
        if item_id:
            item_index = int(item_id) - 1
            if 0 <= item_index < len(self.results):
                video_url = self.results[item_index].url
                webbrowser.open(video_url)
    
    def _toggle_item_selection(self, item_id: str) -> None:
        """Toggle selection of an item."""
        try:
            item_index = int(item_id) - 1
            if 0 <= item_index < len(self.results):
                result = self.results[item_index]
                result.selected = not result.selected
                
                if result.selected:
                    self.selected_items.add(result.video_id)
                else:
                    self.selected_items.discard(result.video_id)
                
                self._refresh_table()
                self._update_controls_state()
        except (ValueError, IndexError):
            pass
    
    def _show_context_menu(self, event) -> None:
        """Show context menu."""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            
            # Create context menu
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(label="Open in Browser", command=lambda: self._on_item_double_click(event))
            context_menu.add_separator()
            context_menu.add_command(label="Select", command=lambda: self._toggle_item_selection(item_id))
            context_menu.add_separator()
            context_menu.add_command(label="Copy URL", command=lambda: self._copy_url(item_id))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def _copy_url(self, item_id: str) -> None:
        """Copy video URL to clipboard."""
        try:
            item_index = int(item_id) - 1
            if 0 <= item_index < len(self.results):
                url = self.results[item_index].url
                self.clipboard_clear()
                self.clipboard_append(url)
        except (ValueError, IndexError):
            pass
    
    def _update_controls_state(self) -> None:
        """Update control buttons state."""
        has_results = len(self.results) > 0
        has_selection = len(self.selected_items) > 0
        
        # Enable/disable buttons
        state = "normal" if has_results else "disabled"
        self.select_all_btn.configure(state=state)
        self.select_none_btn.configure(state=state)
        self.invert_selection_btn.configure(state=state)
        
        download_state = "normal" if has_selection else "disabled"
        self.download_selected_btn.configure(state=download_state)
        
        # Update status labels
        selected_count = len(self.selected_items)
        total_count = len(self.results)
        self.selection_label.configure(text=f"{selected_count} of {total_count} selected")
    
    def _refresh_table(self) -> None:
        """Refresh table display."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add results
        for i, result in enumerate(self.results, 1):
            select_text = "☑️" if result.selected else "☐"
            thumbnail_text = "🖼️"  # Placeholder for thumbnail
            
            # Format duration
            duration_text = self._format_duration(result.duration)
            
            # Format view count
            views_text = self._format_number(result.view_count)
            
            # Format upload date
            date_text = result.upload_date[:10] if result.upload_date else "Unknown"
            
            # Truncate title if too long
            title_text = result.title[:50] + "..." if len(result.title) > 50 else result.title
            
            # Truncate uploader if too long
            uploader_text = result.uploader[:20] + "..." if len(result.uploader) > 20 else result.uploader
            
            self.tree.insert("", "end", iid=str(i), values=(
                select_text,
                thumbnail_text,
                title_text,
                duration_text,
                uploader_text,
                views_text,
                date_text
            ))
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS."""
        if seconds <= 0:
            return "0:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def _format_number(self, num: int) -> str:
        """Format large numbers with K/M/B suffixes."""
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)
    
    def set_results(self, results: List[Dict[str, Any]]) -> None:
        """Set search results to display."""
        self.loading_label.configure(text="")
        
        # Convert dict results to VideoResultItem objects
        self.results = [VideoResultItem(result) for result in results]
        self.selected_items.clear()
        
        # Update display
        if self.results:
            self._show_placeholder(False)
            self._refresh_table()
            self.count_label.configure(text=f"{len(self.results)} results found")
        else:
            self._show_placeholder(True)
            self.count_label.configure(text="No results found")
        
        self._update_controls_state()
    
    def clear_results(self) -> None:
        """Clear all results."""
        self.results.clear()
        self.selected_items.clear()
        self._show_placeholder(True)
        self.count_label.configure(text="No results")
        self._update_controls_state()
        self.loading_label.configure(text="")
    
    def set_loading(self, message: str = "Searching...") -> None:
        """Show loading state."""
        self.loading_label.configure(text=message)
        self.clear_results()
    
    def get_selected_results(self) -> List[VideoResultItem]:
        """Get currently selected video results."""
        return [r for r in self.results if r.selected]
    
    def select_by_video_ids(self, video_ids: List[str]) -> None:
        """Select items by video IDs."""
        self.selected_items.clear()
        for result in self.results:
            if result.video_id in video_ids:
                result.selected = True
                self.selected_items.add(result.video_id)
            else:
                result.selected = False
        
        self._refresh_table()
        self._update_controls_state() 