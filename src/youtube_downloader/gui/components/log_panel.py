"""
Log Panel Component

Displays application logs with basic filtering and formatting.
"""

import customtkinter as ctk
import tkinter as tk
from typing import List
from datetime import datetime

from ..styles.themes import theme_manager


class LogPanel(ctk.CTkFrame):
    """Simple log display panel."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.log_entries = []
        self.max_entries = 500
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Application Logs",
            font=theme_manager.get_font("subheading")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        clear_button = ctk.CTkButton(
            header_frame,
            text="Clear",
            width=80,
            height=28,
            command=self.clear_logs,
            fg_color=theme_manager.get_color("secondary"),
            hover_color=theme_manager.get_color("secondary_hover")
        )
        clear_button.grid(row=0, column=1, sticky="e")
        
        # Log display
        self.log_text = ctk.CTkTextbox(
            self,
            height=150,
            font=theme_manager.get_font("mono"),
            wrap="word"
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
    
    def add_log(self, level: str, message: str) -> None:
        """Add a log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {level:8} | {message}\n"
        
        self.log_text.insert("end", log_line)
        self.log_text.see("end")
        
        # Keep only recent entries
        if len(self.log_entries) >= self.max_entries:
            self.log_entries = self.log_entries[100:]  # Remove oldest 100
            self._refresh_display()
        
        self.log_entries.append({"timestamp": timestamp, "level": level, "message": message})
    
    def clear_logs(self) -> None:
        """Clear all logs."""
        self.log_text.delete("1.0", "end")
        self.log_entries.clear()
        self.add_log("INFO", "Log history cleared")
    
    def _refresh_display(self) -> None:
        """Refresh the display."""
        self.log_text.delete("1.0", "end")
        for entry in self.log_entries:
            log_line = f"[{entry['timestamp']}] {entry['level']:8} | {entry['message']}\n"
            self.log_text.insert("end", log_line) 