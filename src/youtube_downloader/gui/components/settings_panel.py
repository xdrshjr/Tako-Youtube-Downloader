"""
Settings Panel Component

Provides user-friendly controls for download settings including
quality selection, format options, and output directory management.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from pathlib import Path

from ..styles.themes import theme_manager
from ...core.config import DownloadConfig


class SettingsPanel(ctk.CTkFrame):
    """
    Modern settings panel for download configuration.
    
    Features:
    - Video quality selection
    - Output format selection
    - Output directory browser
    - Real-time validation
    - Settings persistence
    """
    
    def __init__(self, parent, on_settings_changed: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize settings panel.
        
        Args:
            parent: Parent widget
            on_settings_changed: Callback function called when settings change
        """
        super().__init__(parent)
        
        self.on_settings_changed = on_settings_changed
        self.current_settings = {
            "quality": "best",
            "format": "mp4",
            "output_directory": str(Path.home() / "Downloads" / "YouTube"),
            "audio_format": "mp3",
            "create_subdirs": False
        }
        
        self._setup_ui()
        self._setup_bindings()
        self._validate_output_directory()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Download Settings",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("text_primary")
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", 
                        padx=12,
                        pady=(8, 4))
        
        # Quality section
        self._create_quality_section()
        
        # Format section
        self._create_format_section()
        
        # Output directory section
        self._create_output_section()
        
        # Advanced options section
        self._create_advanced_section()
    
    def _create_quality_section(self) -> None:
        """Create video quality selection section."""
        row = 1
        
        # Quality label
        quality_label = ctk.CTkLabel(
            self,
            text="Video Quality",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        quality_label.grid(
            row=row, column=0,
            sticky="w", padx=12,
            pady=(6, 2)
        )
        
        # Quality options
        quality_frame = ctk.CTkFrame(self)
        quality_frame.grid(
            row=row + 1, column=0, columnspan=2,
            sticky="ew", padx=12,
            pady=(0, 4)
        )
        quality_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.quality_var = tk.StringVar(value="best")
        
        quality_options = [
            ("Best", "best"),
            ("1080p", "1080p"),
            ("720p", "720p"),
            ("480p", "480p"),
            ("360p", "360p"),
            ("Worst", "worst")
        ]
        
        for i, (text, value) in enumerate(quality_options):
            col = i % 3
            row_num = i // 3
            
            radio_btn = ctk.CTkRadioButton(
                quality_frame,
                text=text,
                variable=self.quality_var,
                value=value,
                font=theme_manager.get_font("small"),
                command=self._on_quality_changed
            )
            radio_btn.grid(
                row=row_num, column=col,
                sticky="w", padx=6,
                pady=2
            )
    
    def _create_format_section(self) -> None:
        """Create output format selection section."""
        row = 3
        
        # Format label
        format_label = ctk.CTkLabel(
            self,
            text="Output Format",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        format_label.grid(
            row=row, column=0,
            sticky="w", padx=12,
            pady=(8, 4)
        )
        
        # Format options frame
        format_frame = ctk.CTkFrame(self)
        format_frame.grid(
            row=row + 1, column=0, columnspan=2,
            sticky="ew", padx=12,
            pady=(0, 8)
        )
        format_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Video format selection
        video_format_frame = ctk.CTkFrame(format_frame)
        video_format_frame.grid(
            row=0, column=0,
            sticky="ew", padx=8,
            pady=8
        )
        
        video_format_label = ctk.CTkLabel(
            video_format_frame,
            text="Video Format",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        video_format_label.grid(row=0, column=0, sticky="w", padx=8)
        
        self.format_combo = ctk.CTkComboBox(
            video_format_frame,
            values=["mp4", "webm", "mkv"],
            state="readonly",
            command=self._on_format_changed,
            font=theme_manager.get_font("body")
        )
        self.format_combo.set("mp4")
        self.format_combo.grid(
            row=1, column=0,
            sticky="ew", padx=8,
            pady=(4, 8)
        )
        
        # Audio format selection
        audio_format_frame = ctk.CTkFrame(format_frame)
        audio_format_frame.grid(
            row=0, column=1,
            sticky="ew", padx=8,
            pady=8
        )
        
        audio_format_label = ctk.CTkLabel(
            audio_format_frame,
            text="Audio Format",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        audio_format_label.grid(row=0, column=0, sticky="w", padx=8)
        
        self.audio_format_combobox = ctk.CTkComboBox(
            audio_format_frame,
            values=["mp3", "aac", "m4a", "ogg"],
            state="readonly",
            command=self._on_audio_format_changed,
            font=theme_manager.get_font("body")
        )
        self.audio_format_combobox.set("mp3")
        self.audio_format_combobox.grid(
            row=1, column=0,
            sticky="ew", padx=8,
            pady=(4, 8)
        )
    
    def _create_output_section(self) -> None:
        """Create output directory selection section."""
        row = 5
        
        # Output directory label
        output_label = ctk.CTkLabel(
            self,
            text="Output Directory",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        output_label.grid(
            row=row, column=0,
            sticky="w", padx=12,
            pady=(8, 4)
        )
        
        # Output directory frame
        output_frame = ctk.CTkFrame(self)
        output_frame.grid(
            row=row + 1, column=0, columnspan=2,
            sticky="ew", padx=12,
            pady=(0, 8)
        )
        output_frame.grid_columnconfigure(0, weight=1)
        
        # Directory path display
        self.output_entry = ctk.CTkEntry(
            output_frame,
            placeholder_text="Select output directory...",
            font=theme_manager.get_font("body"),
            height=32
        )
        self.output_entry.grid(
            row=0, column=0,
            sticky="ew", padx=8,
            pady=8
        )
        self.output_entry.insert(0, self.current_settings["output_directory"])
        
        # Browse button
        self.browse_button = ctk.CTkButton(
            output_frame,
            text="📁 Browse",
            width=80,
            height=32,
            font=theme_manager.get_font("small"),
            command=self._browse_directory
        )
        self.browse_button.grid(
            row=0, column=1,
            padx=(8, 8),
            pady=8
        )
        
        # Create directory button
        self.create_button = ctk.CTkButton(
            output_frame,
            text="📝 Create",
            width=80,
            height=32,
            font=theme_manager.get_font("small"),
            command=self._create_output_directory,
            fg_color=theme_manager.get_color("secondary"),
            hover_color=theme_manager.get_color("secondary_hover")
        )
        self.create_button.grid(
            row=0, column=2,
            padx=(0, 8),
            pady=8
        )
        
        # Directory status
        self.dir_status_label = ctk.CTkLabel(
            output_frame,
            text="",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.dir_status_label.grid(
            row=1, column=0, columnspan=3,
            sticky="w", padx=8,
            pady=(0, 8)
        )
    
    def _create_advanced_section(self) -> None:
        """Create advanced options section."""
        row = 7
        
        # Advanced options label
        advanced_label = ctk.CTkLabel(
            self,
            text="Advanced Options",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        advanced_label.grid(
            row=row, column=0,
            sticky="w", padx=12,
            pady=(8, 4)
        )
        
        # Advanced options frame
        advanced_frame = ctk.CTkFrame(self)
        advanced_frame.grid(
            row=row + 1, column=0, columnspan=2,
            sticky="ew", padx=12,
            pady=(0, 12)
        )
        
        # Create subdirectories checkbox
        self.create_subdirs_var = tk.BooleanVar(value=self.current_settings["create_subdirs"])
        self.create_subdirs_checkbox = ctk.CTkCheckBox(
            advanced_frame,
            text="Create subdirectories by channel",
            variable=self.create_subdirs_var,
            font=theme_manager.get_font("small"),
            command=self._on_subdirs_changed
        )
        self.create_subdirs_checkbox.grid(
            row=0, column=0,
            sticky="w", padx=8,
            pady=8
        )
    
    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        # Bind output directory entry changes
        self.output_entry.bind("<KeyRelease>", self._on_output_changed)
        self.output_entry.bind("<FocusOut>", self._on_output_changed)
    
    def _on_quality_changed(self) -> None:
        """Handle quality selection change."""
        self.current_settings["quality"] = self.quality_var.get()
        self._notify_change()
    
    def _on_format_changed(self, value: str) -> None:
        """Handle format selection change."""
        self.current_settings["format"] = value
        self._notify_change()
    
    def _on_audio_format_changed(self, value: str) -> None:
        """Handle audio format selection change."""
        self.current_settings["audio_format"] = value
        self._notify_change()
    
    def _on_output_changed(self, event=None) -> None:
        """Handle output directory path change."""
        path = self.output_entry.get().strip()
        if path != self.current_settings["output_directory"]:
            self.current_settings["output_directory"] = path
            self._validate_output_directory()
            self._notify_change()
    
    def _on_subdirs_changed(self) -> None:
        """Handle subdirectories option change."""
        self.current_settings["create_subdirs"] = self.create_subdirs_var.get()
        self._notify_change()
    
    def _browse_directory(self) -> None:
        """Open directory browser."""
        current_dir = self.output_entry.get().strip()
        if not current_dir or not os.path.exists(current_dir):
            current_dir = str(Path.home())
        
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=current_dir
        )
        
        if selected_dir:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, selected_dir)
            self._on_output_changed()
    
    def _create_output_directory(self) -> None:
        """Create the output directory if it doesn't exist."""
        path = self.output_entry.get().strip()
        if not path:
            messagebox.showwarning("Invalid Path", "Please enter a directory path")
            return
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            self._validate_output_directory()
            messagebox.showinfo("Success", f"Directory created successfully:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create directory:\n{str(e)}")
    
    def _validate_output_directory(self) -> None:
        """Validate the output directory."""
        path = self.output_entry.get().strip()
        
        if not path:
            self.dir_status_label.configure(
                text="No directory specified",
                text_color=theme_manager.get_color("warning")
            )
            return
        
        path_obj = Path(path)
        
        if path_obj.exists() and path_obj.is_dir():
            # Check write permissions
            if os.access(path, os.W_OK):
                self.dir_status_label.configure(
                    text="✓ Directory exists and is writable",
                    text_color=theme_manager.get_color("success")
                )
            else:
                self.dir_status_label.configure(
                    text="⚠ Directory exists but is not writable",
                    text_color=theme_manager.get_color("warning")
                )
        else:
            parent_dir = path_obj.parent
            if parent_dir.exists() and os.access(parent_dir, os.W_OK):
                self.dir_status_label.configure(
                    text="📁 Directory will be created",
                    text_color=theme_manager.get_color("info")
                )
            else:
                self.dir_status_label.configure(
                    text="✗ Invalid path or parent directory not accessible",
                    text_color=theme_manager.get_color("error")
                )
    
    def _notify_change(self) -> None:
        """Notify parent of settings change."""
        if self.on_settings_changed:
            self.on_settings_changed(self.current_settings.copy())
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        return self.current_settings.copy()
    
    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set settings programmatically."""
        # Update internal settings
        self.current_settings.update(settings)
        
        # Update UI controls
        if "quality" in settings:
            self.quality_var.set(settings["quality"])
        
        if "format" in settings:
            self.format_combo.set(settings["format"])
        
        if "audio_format" in settings:
            self.audio_format_combobox.set(settings["audio_format"])
        
        if "output_directory" in settings:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, settings["output_directory"])
            self._validate_output_directory()
        
        if "create_subdirs" in settings:
            self.create_subdirs_var.set(settings["create_subdirs"])
    
    def get_download_config(self) -> DownloadConfig:
        """Create DownloadConfig object from current settings."""
        config = DownloadConfig()
        config.quality = self.current_settings["quality"]
        config.format = self.current_settings["format"]
        config.output_directory = self.current_settings["output_directory"]
        return config 