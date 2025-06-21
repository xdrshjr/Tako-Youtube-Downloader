"""
Main Window for YouTube Downloader GUI

The primary application window that orchestrates all components
and provides the main user interface for the YouTube downloader.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import logging
from typing import Optional, Dict, Any
import sys
import os

# Import components
from .components.url_input import URLInputPanel
from .components.settings_panel import SettingsPanel
from .components.progress_panel import ProgressPanel
from .components.log_panel import LogPanel
from .components.video_info_panel import VideoInfoPanel
from .styles.themes import theme_manager

# Import core functionality
from ..core.validator import URLValidator
from ..core.downloader import VideoDownloader
from ..core.config import ConfigManager


class YouTubeDownloaderApp(ctk.CTk):
    """
    Main application window for YouTube Downloader.
    
    Features:
    - Modern, responsive design
    - Integrated download management
    - Real-time progress tracking
    - Comprehensive logging
    - Theme switching
    - Settings persistence
    """
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        
        # Application state
        self.current_url = ""
        self.download_thread = None
        self.downloader = None
        self.is_downloading = False
        
        # Initialize core components
        self.validator = URLValidator()
        self.config_manager = ConfigManager()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize UI
        self._setup_window()
        self._setup_ui()
        self._setup_bindings()
        
        # Apply theme
        theme_manager.configure_ctk_theme()
        
        # Initialize with welcome message
        self._show_welcome_message()
    
    def _setup_window(self) -> None:
        """Configure the main window properties."""
        # Window configuration
        self.title("TakoAI YouTube Downloader - Professional Media Solutions")
        self.geometry("1400x950")
        self.minsize(1350, 850)
        
        # Center window on screen
        self._center_window()
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Set window icon (if available)
        try:
            # You can add an icon file here
            # self.iconbitmap("icon.ico")
            pass
        except:
            pass
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    
    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        # Configure main window grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar frame - fixed width, full height
        self.sidebar = ctk.CTkFrame(self, width=420, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)  # Allow content to expand
        # Configure rows: 0=branding, 1=url, 2=settings(expandable), 3=buttons(fixed), 4=theme(fixed)
        self.sidebar.grid_rowconfigure(2, weight=1)  # Only settings panel can expand/shrink
        self.sidebar.grid_rowconfigure(3, weight=0)  # Buttons always visible
        self.sidebar.grid_rowconfigure(4, weight=0)  # Theme always visible
        
        # Main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create sidebar components
        self._create_sidebar()
        
        # Create main content components
        self._create_main_content()
        
        # Create menu bar
        self._create_menu_bar()
    
    def _create_sidebar(self) -> None:
        """Create sidebar with controls and settings."""
        # TakoAI Branding - Compact Version
        branding_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        branding_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        branding_frame.grid_columnconfigure(1, weight=1)
        
        # Compact logo and brand in one line
        logo_label = ctk.CTkLabel(
            branding_frame,
            text="🐙",  # Octopus emoji for TakoAI
            font=("Segoe UI Emoji", 20),
            text_color=theme_manager.get_color("accent")
        )
        logo_label.grid(row=0, column=0, padx=(0, 8))
        
        # Brand and app title combined
        title_label = ctk.CTkLabel(
            branding_frame,
            text="TakoAI YouTube Downloader",
            font=theme_manager.get_font("heading"),
            text_color=theme_manager.get_color("accent")
        )
        title_label.grid(row=0, column=1, sticky="w")
        
        # Compact version info
        version_label = ctk.CTkLabel(
            branding_frame,
            text="v1.0 • Intelligent Media Solutions",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        version_label.grid(row=1, column=1, sticky="w", pady=(2, 0))
        
        # URL Input Panel
        self.url_panel = URLInputPanel(
            self.sidebar,
            on_url_changed=self._on_url_changed
        )
        self.url_panel.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 5))
        
        # Settings Panel
        self.settings_panel = SettingsPanel(
            self.sidebar,
            on_settings_changed=self._on_settings_changed
        )
        self.settings_panel.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        # Action buttons frame - PRIORITY SECTION
        buttons_frame = ctk.CTkFrame(self.sidebar)
        buttons_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(5, 5))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Download button - MAIN ACTION
        self.download_button = ctk.CTkButton(
            buttons_frame,
            text="🔽 Download",
            height=32,
            font=theme_manager.get_font("body"),
            command=self._start_download,
            state="disabled"
        )
        self.download_button.grid(row=0, column=0, columnspan=2, sticky="ew", 
                                 padx=8, pady=8)
        
        # Info and Cancel buttons
        self.info_button = ctk.CTkButton(
            buttons_frame,
            text="ℹ️ Info",
            height=26,
            font=theme_manager.get_font("small"),
            command=self._fetch_video_info,
            fg_color=theme_manager.get_color("secondary"),
            hover_color=theme_manager.get_color("secondary_hover"),
            state="disabled"
        )
        self.info_button.grid(row=1, column=0, sticky="ew", 
                             padx=(8, 4), pady=(0, 8))
        
        self.cancel_button = ctk.CTkButton(
            buttons_frame,
            text="✕ Cancel",
            height=26,
            font=theme_manager.get_font("small"),
            command=self._cancel_download,
            fg_color=theme_manager.get_color("error"),
            hover_color="#c0392b",
            state="disabled"
        )
        self.cancel_button.grid(row=1, column=1, sticky="ew", 
                               padx=(4, 8), pady=(0, 8))
        
        # Theme toggle - Compact
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 10))
        theme_frame.grid_columnconfigure(1, weight=1)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        theme_label.grid(row=0, column=0, sticky="w")
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark Mode",
            command=self._toggle_theme,
            font=theme_manager.get_font("small")
        )
        self.theme_switch.grid(row=0, column=1, sticky="e", padx=(8, 0))
        self.theme_switch.select()  # Default to dark theme
    
    def _create_main_content(self) -> None:
        """Create main content area."""
        # Video Info Panel
        self.video_info_panel = VideoInfoPanel(self.main_frame)
        self.video_info_panel.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Content tabs or panels frame
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Progress Panel
        self.progress_panel = ProgressPanel(content_frame)
        self.progress_panel.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Log Panel
        self.log_panel = LogPanel(content_frame)
        self.log_panel.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
    
    def _create_menu_bar(self) -> None:
        """Create application menu bar."""
        # Note: CustomTkinter doesn't have native menu support
        # This could be implemented with a custom frame if needed
        pass
    
    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        # Window close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Keyboard shortcuts
        self.bind("<Control-q>", lambda e: self._on_closing())
        self.bind("<Control-o>", lambda e: self._fetch_video_info())
        self.bind("<Control-d>", lambda e: self._start_download() if not self.is_downloading else None)
        self.bind("<Escape>", lambda e: self._cancel_download() if self.is_downloading else None)
    
    def _show_welcome_message(self) -> None:
        """Show welcome message in logs."""
        self.log_panel.add_log("INFO", "🐙 TakoAI YouTube Downloader GUI started successfully")
        self.log_panel.add_log("INFO", "✨ Professional Media Solutions - Ready to serve")
        self.log_panel.add_log("INFO", "📝 Enter a YouTube URL to begin downloading")
        self.log_panel.add_log("INFO", "⌨️ Keyboard shortcuts: Ctrl+O (Info), Ctrl+D (Download), Ctrl+Q (Quit)")
        self.log_panel.add_log("INFO", "🎯 Powered by TakoAI - Intelligent Media Solutions")
    
    def _on_url_changed(self, url: str, is_valid: bool) -> None:
        """Handle URL input changes."""
        self.current_url = url
        
        # Update button states
        self.info_button.configure(state="normal" if is_valid else "disabled")
        self.download_button.configure(state="normal" if is_valid and not self.is_downloading else "disabled")
        
        # Clear video info if URL changed
        if not is_valid:
            self.video_info_panel.clear_info()
        
        # Log URL validation
        if url:
            if is_valid:
                self.log_panel.add_log("INFO", f"Valid YouTube URL detected")
            else:
                self.log_panel.add_log("WARNING", "Invalid YouTube URL format")
    
    def _on_settings_changed(self, settings: Dict[str, Any]) -> None:
        """Handle settings changes."""
        self.log_panel.add_log("DEBUG", f"Settings updated: {settings}")
    
    def _fetch_video_info(self) -> None:
        """Fetch video information in background thread."""
        if not self.current_url:
            messagebox.showwarning("No URL", "Please enter a YouTube URL first")
            return
        
        self.video_info_panel.set_loading()
        self.progress_panel.set_fetching_info()
        self.log_panel.add_log("INFO", "Fetching video information...")
        
        def fetch_info():
            try:
                # Create temporary downloader for info fetching
                config = self.settings_panel.get_download_config()
                downloader = VideoDownloader(config)
                
                # Get video info
                video_info = downloader.get_video_info(self.current_url)
                
                # Update UI in main thread
                self.after(0, lambda: self._on_video_info_received(video_info))
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self._on_video_info_error(error_msg))
        
        # Start fetch thread
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def _on_video_info_received(self, video_info) -> None:
        """Handle received video information."""
        self.video_info_panel.set_video_info(video_info)
        self.progress_panel.set_ready("Video information loaded")
        self.log_panel.add_log("INFO", f"Video info loaded: {video_info.title}")
    
    def _on_video_info_error(self, error_message: str) -> None:
        """Handle video info fetch error."""
        self.video_info_panel.set_error(f"Error: {error_message}")
        self.progress_panel.set_ready("Failed to load video information")
        self.log_panel.add_log("ERROR", f"Failed to fetch video info: {error_message}")
        messagebox.showerror("Error", f"Failed to fetch video information:\n{error_message}")
    
    def _start_download(self) -> None:
        """Start video download."""
        if not self.current_url:
            messagebox.showwarning("No URL", "Please enter a YouTube URL first")
            return
        
        if self.is_downloading:
            messagebox.showinfo("Download in Progress", "A download is already in progress")
            return
        
        # Update UI state
        self.is_downloading = True
        self._update_button_states()
        
        # Prepare for download
        self.progress_panel.set_preparing("Preparing download...")
        self.log_panel.add_log("INFO", f"Starting download: {self.current_url}")
        
        # Start download thread
        self.download_thread = threading.Thread(target=self._download_worker, daemon=True)
        self.download_thread.start()
    
    def _download_worker(self) -> None:
        """Worker thread for downloading videos."""
        try:
            # Get current settings
            config = self.settings_panel.get_download_config()
            
            # Create downloader with progress callback
            self.downloader = VideoDownloader(config)
            self.downloader.set_progress_callback(self._progress_callback)
            
            # Start download
            result = self.downloader.download_video(self.current_url)
            
            # Handle result in main thread
            self.after(0, lambda: self._on_download_complete(result))
            
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._on_download_error(error_msg))
    
    def _progress_callback(self, data: Dict[str, Any]) -> None:
        """Handle download progress updates."""
        # Update progress in main thread
        self.after(0, lambda: self.progress_panel.update_progress(data))
        
        # Log progress
        status = data.get('status', 'unknown')
        if status == 'downloading' and '_percent_str' in data:
            percent = data['_percent_str']
            filename = data.get('filename', 'video')
            self.after(0, lambda: self.log_panel.add_log("INFO", f"Downloading {filename}: {percent}"))
    
    def _on_download_complete(self, result) -> None:
        """Handle download completion."""
        self.is_downloading = False
        self._update_button_states()
        
        if result.success:
            self.log_panel.add_log("INFO", f"Download completed: {result.output_path}")
            messagebox.showinfo("Download Complete", 
                               f"Video downloaded successfully!\n\nLocation: {result.output_path}")
        else:
            self.log_panel.add_log("ERROR", f"Download failed: {result.error_message}")
            messagebox.showerror("Download Failed", 
                                f"Download failed:\n{result.error_message}")
    
    def _on_download_error(self, error_message: str) -> None:
        """Handle download error."""
        self.is_downloading = False
        self._update_button_states()
        
        self.progress_panel._update_error({"error": error_message})
        self.log_panel.add_log("ERROR", f"Download error: {error_message}")
        messagebox.showerror("Download Error", f"An error occurred during download:\n{error_message}")
    
    def _cancel_download(self) -> None:
        """Cancel current download."""
        if not self.is_downloading:
            return
        
        self.log_panel.add_log("WARNING", "Download cancelled by user")
        
        # TODO: Implement proper download cancellation
        # This would require extending the downloader to support cancellation
        self.is_downloading = False
        self._update_button_states()
        
        self.progress_panel.set_ready("Download cancelled")
        messagebox.showinfo("Cancelled", "Download has been cancelled")
    
    def _update_button_states(self) -> None:
        """Update button states based on current application state."""
        url_valid = bool(self.current_url and self.url_panel.is_url_valid())
        
        if self.is_downloading:
            self.download_button.configure(state="disabled")
            self.info_button.configure(state="disabled")
            self.cancel_button.configure(state="normal")
        else:
            self.download_button.configure(state="normal" if url_valid else "disabled")
            self.info_button.configure(state="normal" if url_valid else "disabled")
            self.cancel_button.configure(state="disabled")
    
    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self.theme_switch.get():
            theme_manager.set_theme("dark")
            self.log_panel.add_log("INFO", "Switched to dark theme")
        else:
            theme_manager.set_theme("light")
            self.log_panel.add_log("INFO", "Switched to light theme")
        
        # Reconfigure theme
        theme_manager.configure_ctk_theme()
    
    def _on_closing(self) -> None:
        """Handle application closing."""
        if self.is_downloading:
            if messagebox.askokcancel("Download in Progress", 
                                    "A download is in progress. Are you sure you want to quit?"):
                self.log_panel.add_log("WARNING", "Application closed during download")
                self.destroy()
        else:
            self.log_panel.add_log("INFO", "Application closing")
            self.destroy()


def run_gui():
    """Main entry point for the GUI application."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run application
    app = YouTubeDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui() 