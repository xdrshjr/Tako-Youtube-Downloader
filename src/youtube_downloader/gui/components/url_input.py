"""
URL Input Component

Provides a modern, user-friendly interface for YouTube URL input with
real-time validation, visual feedback, and paste support.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Callable, Optional
import threading
import re

from ..styles.themes import theme_manager
from ...core.validator import URLValidator


class URLInputPanel(ctk.CTkFrame):
    """
    Modern URL input panel with validation and visual feedback.
    
    Features:
    - Real-time URL validation
    - Visual feedback for valid/invalid URLs
    - Paste from clipboard support
    - Clear button
    - Loading state indication
    """
    
    def __init__(self, parent, on_url_changed: Optional[Callable[[str, bool], None]] = None):
        """
        Initialize URL input panel.
        
        Args:
            parent: Parent widget
            on_url_changed: Callback function called when URL changes (url, is_valid)
        """
        super().__init__(parent)
        
        self.validator = URLValidator()
        self.on_url_changed = on_url_changed
        self.current_url = ""
        self.is_valid = False
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text="YouTube Video URL",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("text_primary")
        )
        self.title_label.grid(
            row=0, column=0, columnspan=3,
            sticky="w", padx=12,
            pady=(8, 4)
        )
        
        # URL input frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(
            row=1, column=0, columnspan=3,
            sticky="ew", padx=12,
            pady=(0, 4)
        )
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # URL entry
        self.url_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Paste YouTube video URL here...",
            height=32,
            font=theme_manager.get_font("body"),
            corner_radius=6
        )
        self.url_entry.grid(
            row=0, column=0,
            sticky="ew", padx=6,
            pady=6
        )
        
        # Paste button
        self.paste_button = ctk.CTkButton(
            self.input_frame,
            text="📋 Paste",
            width=70,
            height=32,
            font=theme_manager.get_font("small"),
            command=self._paste_from_clipboard,
            corner_radius=6
        )
        self.paste_button.grid(
            row=0, column=1,
            padx=(0, 6),
            pady=6
        )
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            self.input_frame,
            text="✕ Clear",
            width=70,
            height=32,
            font=theme_manager.get_font("small"),
            command=self._clear_url,
            fg_color=theme_manager.get_color("secondary"),
            hover_color=theme_manager.get_color("secondary_hover"),
            corner_radius=6
        )
        self.clear_button.grid(
            row=0, column=2,
            padx=(0, 6),
            pady=6
        )
        
        # Status frame
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(
            row=2, column=0, columnspan=3,
            sticky="ew", padx=12,
            pady=(0, 4)
        )
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=("Arial", 16),
            text_color=theme_manager.get_color("text_disabled"),
            width=20
        )
        self.status_indicator.grid(row=0, column=0, padx=(0, 8))
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Enter a YouTube video URL to begin",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        self.status_label.grid(row=0, column=1, sticky="w")
        
        # Help label
        self.help_label = ctk.CTkLabel(
            self,
            text="Supported formats: youtube.com/watch?v=..., youtu.be/..., youtube.com/shorts/...",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_disabled")
        )
        self.help_label.grid(
            row=3, column=0, columnspan=3,
            sticky="w", padx=12,
            pady=(0, 4)
        )
    
    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        # Bind URL entry events
        self.url_entry.bind("<KeyRelease>", self._on_url_changed)
        self.url_entry.bind("<FocusOut>", self._on_url_changed)
        self.url_entry.bind("<Control-v>", self._on_paste_event)
        
        # Enable drag and drop (basic implementation)
        self.url_entry.bind("<Button-1>", lambda e: self.url_entry.focus_set())
    
    def _on_url_changed(self, event=None) -> None:
        """Handle URL input changes."""
        url = self.url_entry.get().strip()
        
        if url != self.current_url:
            self.current_url = url
            self._validate_url_async(url)
    
    def _on_paste_event(self, event=None) -> None:
        """Handle paste event."""
        # Small delay to allow paste to complete
        self.after(50, self._on_url_changed)
    
    def _validate_url_async(self, url: str) -> None:
        """Validate URL asynchronously to avoid blocking UI."""
        if not url:
            self._update_status("", False, "Enter a YouTube video URL to begin")
            return
        
        # Show validating status
        self._update_status("validating", None, "Validating URL...")
        
        # Perform validation in background thread
        def validate():
            try:
                is_valid = self.validator.validate_youtube_url(url)
                video_id = None
                
                if is_valid:
                    video_id = self.validator.extract_video_id(url)
                
                # Update UI in main thread
                self.after(0, lambda: self._validation_complete(url, is_valid, video_id))
                
            except Exception as e:
                self.after(0, lambda: self._validation_error(str(e)))
        
        # Start validation thread
        threading.Thread(target=validate, daemon=True).start()
    
    def _validation_complete(self, url: str, is_valid: bool, video_id: Optional[str]) -> None:
        """Handle validation completion."""
        if url != self.current_url:
            return  # URL changed while validating
        
        self.is_valid = is_valid
        
        if is_valid:
            message = f"Valid YouTube URL (ID: {video_id})" if video_id else "Valid YouTube URL"
            self._update_status("valid", True, message)
        else:
            self._update_status("invalid", False, "Invalid YouTube URL format")
        
        # Notify parent component
        if self.on_url_changed:
            self.on_url_changed(url, is_valid)
    
    def _validation_error(self, error_message: str) -> None:
        """Handle validation error."""
        self.is_valid = False
        self._update_status("error", False, f"Validation error: {error_message}")
        
        if self.on_url_changed:
            self.on_url_changed(self.current_url, False)
    
    def _update_status(self, status_type: str, is_valid: Optional[bool], message: str) -> None:
        """Update status indicator and message."""
        # Status colors and indicators
        status_config = {
            "": {"color": theme_manager.get_color("text_disabled"), "indicator": "●"},
            "validating": {"color": theme_manager.get_color("info"), "indicator": "⟳"},
            "valid": {"color": theme_manager.get_color("success"), "indicator": "✓"},
            "invalid": {"color": theme_manager.get_color("error"), "indicator": "✗"},
            "error": {"color": theme_manager.get_color("error"), "indicator": "⚠"}
        }
        
        config = status_config.get(status_type, status_config[""])
        
        # Update indicator
        self.status_indicator.configure(
            text=config["indicator"],
            text_color=config["color"]
        )
        
        # Update message
        self.status_label.configure(
            text=message,
            text_color=config["color"]
        )
        
        # Update entry border color if validation complete
        if is_valid is not None:
            border_color = theme_manager.get_color("success") if is_valid else theme_manager.get_color("error")
            try:
                self.url_entry.configure(border_color=border_color)
            except:
                pass  # Border color might not be supported in all versions
    
    def _paste_from_clipboard(self) -> None:
        """Paste URL from clipboard."""
        try:
            clipboard_text = self.clipboard_get().strip()
            if clipboard_text:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_text)
                self._on_url_changed()
        except tk.TclError:
            messagebox.showwarning("Clipboard Error", "Could not access clipboard")
    
    def _clear_url(self) -> None:
        """Clear the URL input."""
        self.url_entry.delete(0, tk.END)
        self.current_url = ""
        self.is_valid = False
        self._update_status("", False, "Enter a YouTube video URL to begin")
        
        if self.on_url_changed:
            self.on_url_changed("", False)
    
    def get_url(self) -> str:
        """Get the current URL."""
        return self.current_url
    
    def is_url_valid(self) -> bool:
        """Check if current URL is valid."""
        return self.is_valid
    
    def set_url(self, url: str) -> None:
        """Set URL programmatically."""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self._on_url_changed()
    
    def enable(self) -> None:
        """Enable the input panel."""
        self.url_entry.configure(state="normal")
        self.paste_button.configure(state="normal")
        self.clear_button.configure(state="normal")
    
    def disable(self) -> None:
        """Disable the input panel."""
        self.url_entry.configure(state="disabled")
        self.paste_button.configure(state="disabled")
        self.clear_button.configure(state="disabled") 