"""
Search Panel Component

Provides user-friendly controls for YouTube video search including
keyword input, filtering options, and search parameters configuration.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from pathlib import Path

from ..styles.themes import theme_manager
from ...core.search_config import SearchConfig, FilterConfig


class SearchPanel(ctk.CTkFrame):
    """
    Modern search panel for YouTube video search configuration.
    
    Features:
    - Search keyword input
    - Download quantity selection (1-100)
    - Duration limits (min/max sliders)
    - Sort order selection (relevance/upload_date/view_count)
    - Advanced options (upload date filter, exclude shorts/live)
    """
    
    def __init__(self, parent, on_search_clicked: Optional[Callable[[SearchConfig], None]] = None):
        """
        Initialize search panel.
        
        Args:
            parent: Parent widget
            on_search_clicked: Callback function called when search is initiated
        """
        super().__init__(parent)
        
        self.on_search_clicked = on_search_clicked
        self.is_searching = False
        
        # Initialize default search configuration
        self.current_config = SearchConfig()
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="🔍 YouTube Search & Download",
            font=theme_manager.get_font("subheading"),
            text_color=theme_manager.get_color("accent")
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", 
                        padx=12, pady=(12, 8))
        
        # Search keyword section
        self._create_search_section()
        
        # Basic parameters section
        self._create_basic_params_section()
        
        # Duration filters section
        self._create_duration_section()
        
        # Advanced options section
        self._create_advanced_section()
        
        # Search button
        self._create_search_button()
    
    def _create_search_section(self) -> None:
        """Create search keyword input section."""
        row = 1
        
        # Search keyword label
        search_label = ctk.CTkLabel(
            self,
            text="Search Keywords",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        search_label.grid(row=row, column=0, sticky="w", padx=12, pady=(8, 4))
        
        # Search input with placeholder
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter search keywords (e.g. 'python tutorial', 'music covers')",
            font=theme_manager.get_font("body"),
            height=36
        )
        self.search_entry.grid(row=row+1, column=0, columnspan=2, sticky="ew", 
                              padx=12, pady=(0, 8))
    
    def _create_basic_params_section(self) -> None:
        """Create basic parameters section."""
        row = 3
        
        # Basic parameters frame
        params_frame = ctk.CTkFrame(self)
        params_frame.grid(row=row, column=0, columnspan=2, sticky="ew", 
                         padx=12, pady=(4, 8))
        params_frame.grid_columnconfigure(1, weight=1)
        params_frame.grid_columnconfigure(3, weight=1)
        
        # Download quantity
        quantity_label = ctk.CTkLabel(
            params_frame,
            text="Videos to Download:",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        quantity_label.grid(row=0, column=0, sticky="w", padx=12, pady=8)
        
        self.quantity_var = tk.StringVar(value="10")
        self.quantity_spinbox = ctk.CTkEntry(
            params_frame,
            textvariable=self.quantity_var,
            width=80,
            font=theme_manager.get_font("body")
        )
        self.quantity_spinbox.grid(row=0, column=1, sticky="w", padx=(8, 20), pady=8)
        
        # Sort order
        sort_label = ctk.CTkLabel(
            params_frame,
            text="Sort by:",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        sort_label.grid(row=0, column=2, sticky="w", padx=12, pady=8)
        
        self.sort_combo = ctk.CTkComboBox(
            params_frame,
            values=["Relevance", "Upload Date", "View Count", "Rating"],
            state="readonly",
            font=theme_manager.get_font("body"),
            width=120
        )
        self.sort_combo.set("Relevance")
        self.sort_combo.grid(row=0, column=3, sticky="w", padx=(8, 12), pady=8)
    
    def _create_duration_section(self) -> None:
        """Create duration filter section."""
        row = 4
        
        # Duration section label
        duration_label = ctk.CTkLabel(
            self,
            text="Duration Filters",
            font=theme_manager.get_font("body"),
            text_color=theme_manager.get_color("text_primary")
        )
        duration_label.grid(row=row, column=0, sticky="w", padx=12, pady=(8, 4))
        
        # Duration frame
        duration_frame = ctk.CTkFrame(self)
        duration_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", 
                           padx=12, pady=(0, 8))
        duration_frame.grid_columnconfigure(1, weight=1)
        
        # Min duration
        min_dur_label = ctk.CTkLabel(
            duration_frame,
            text="Min Duration (seconds):",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        min_dur_label.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))
        
        self.min_duration_var = tk.StringVar(value="0")
        self.min_duration_entry = ctk.CTkEntry(
            duration_frame,
            textvariable=self.min_duration_var,
            width=100,
            font=theme_manager.get_font("body")
        )
        self.min_duration_entry.grid(row=0, column=1, sticky="w", padx=(8, 12), pady=(8, 4))
        
        # Max duration
        max_dur_label = ctk.CTkLabel(
            duration_frame,
            text="Max Duration (seconds):",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        max_dur_label.grid(row=1, column=0, sticky="w", padx=12, pady=(4, 8))
        
        self.max_duration_var = tk.StringVar(value="3600")  # 1 hour default
        self.max_duration_entry = ctk.CTkEntry(
            duration_frame,
            textvariable=self.max_duration_var,
            width=100,
            font=theme_manager.get_font("body")
        )
        self.max_duration_entry.grid(row=1, column=1, sticky="w", padx=(8, 12), pady=(4, 8))
        
        # Duration presets
        presets_frame = ctk.CTkFrame(duration_frame)
        presets_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(20, 12), pady=8)
        
        presets_label = ctk.CTkLabel(
            presets_frame,
            text="Quick Presets:",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        presets_label.grid(row=0, column=0, columnspan=3, padx=8, pady=(8, 4))
        
        # Preset buttons
        preset_buttons = [
            ("Short (0-4min)", (0, 240)),
            ("Medium (4-20min)", (240, 1200)),
            ("Long (20min+)", (1200, 7200))
        ]
        
        for i, (text, (min_val, max_val)) in enumerate(preset_buttons):
            btn = ctk.CTkButton(
                presets_frame,
                text=text,
                width=90,
                height=24,
                font=theme_manager.get_font("small"),
                command=lambda m=min_val, x=max_val: self._set_duration_preset(m, x)
            )
            btn.grid(row=1, column=i, padx=4, pady=(0, 8))
    
    def _create_advanced_section(self) -> None:
        """Create advanced options section."""
        row = 6
        
        # Advanced options collapsible frame
        self.advanced_frame = ctk.CTkFrame(self)
        self.advanced_frame.grid(row=row, column=0, columnspan=2, sticky="ew", 
                                padx=12, pady=(4, 8))
        self.advanced_frame.grid_columnconfigure(1, weight=1)
        
        # Advanced toggle button
        self.show_advanced = tk.BooleanVar(value=False)
        self.advanced_toggle = ctk.CTkCheckBox(
            self.advanced_frame,
            text="Advanced Options",
            variable=self.show_advanced,
            font=theme_manager.get_font("body"),
            command=self._toggle_advanced_options
        )
        self.advanced_toggle.grid(row=0, column=0, sticky="w", padx=12, pady=8)
        
        # Advanced options content (initially hidden)
        self.advanced_content = ctk.CTkFrame(self.advanced_frame)
        self.advanced_content.grid_columnconfigure((0, 1), weight=1)
        
        # Upload date filter
        upload_date_label = ctk.CTkLabel(
            self.advanced_content,
            text="Upload Date:",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        upload_date_label.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))
        
        self.upload_date_combo = ctk.CTkComboBox(
            self.advanced_content,
            values=["Any Time", "Past Hour", "Today", "This Week", "This Month", "This Year"],
            state="readonly",
            font=theme_manager.get_font("small"),
            width=120
        )
        self.upload_date_combo.set("Any Time")
        self.upload_date_combo.grid(row=0, column=1, sticky="w", padx=(8, 12), pady=(8, 4))
        
        # Content filters
        self.exclude_shorts_var = tk.BooleanVar(value=True)
        self.exclude_shorts_cb = ctk.CTkCheckBox(
            self.advanced_content,
            text="Exclude YouTube Shorts",
            variable=self.exclude_shorts_var,
            font=theme_manager.get_font("small")
        )
        self.exclude_shorts_cb.grid(row=1, column=0, sticky="w", padx=12, pady=4)
        
        self.exclude_live_var = tk.BooleanVar(value=True)
        self.exclude_live_cb = ctk.CTkCheckBox(
            self.advanced_content,
            text="Exclude Live Streams",
            variable=self.exclude_live_var,
            font=theme_manager.get_font("small")
        )
        self.exclude_live_cb.grid(row=1, column=1, sticky="w", padx=12, pady=4)
        
        # Quality filter
        quality_label = ctk.CTkLabel(
            self.advanced_content,
            text="Minimum Quality:",
            font=theme_manager.get_font("small"),
            text_color=theme_manager.get_color("text_secondary")
        )
        quality_label.grid(row=2, column=0, sticky="w", padx=12, pady=(8, 4))
        
        self.min_quality_combo = ctk.CTkComboBox(
            self.advanced_content,
            values=["Any", "360p", "480p", "720p", "1080p"],
            state="readonly",
            font=theme_manager.get_font("small"),
            width=80
        )
        self.min_quality_combo.set("Any")
        self.min_quality_combo.grid(row=2, column=1, sticky="w", padx=(8, 12), pady=(8, 4))
    
    def _create_search_button(self) -> None:
        """Create the main search button."""
        row = 7
        
        # Button frame for proper spacing
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", 
                         padx=12, pady=(8, 12))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Main search button
        self.search_button = ctk.CTkButton(
            button_frame,
            text="🔍 Search & Queue Downloads",
            height=40,
            font=theme_manager.get_font("heading"),
            command=self._on_search_clicked,
            fg_color=theme_manager.get_color("accent"),
            hover_color=theme_manager.get_color("primary_hover")
        )
        self.search_button.grid(row=0, column=0, sticky="ew")
    
    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda e: self._on_search_clicked())
        
        # Bind quantity validation
        self.quantity_spinbox.bind("<KeyRelease>", self._validate_quantity)
        self.quantity_spinbox.bind("<FocusOut>", self._validate_quantity)
        
        # Bind duration validation
        self.min_duration_entry.bind("<KeyRelease>", self._validate_duration)
        self.max_duration_entry.bind("<KeyRelease>", self._validate_duration)
    
    def _toggle_advanced_options(self) -> None:
        """Toggle visibility of advanced options."""
        if self.show_advanced.get():
            self.advanced_content.grid(row=1, column=0, columnspan=2, sticky="ew", 
                                     padx=12, pady=(0, 8))
        else:
            self.advanced_content.grid_remove()
    
    def _set_duration_preset(self, min_duration: int, max_duration: int) -> None:
        """Set duration values from preset."""
        self.min_duration_var.set(str(min_duration))
        self.max_duration_var.set(str(max_duration))
    
    def _validate_quantity(self, event=None) -> None:
        """Validate quantity input."""
        try:
            value = int(self.quantity_var.get())
            if value < 1:
                self.quantity_var.set("1")
            elif value > 100:
                self.quantity_var.set("100")
        except ValueError:
            self.quantity_var.set("10")
    
    def _validate_duration(self, event=None) -> None:
        """Validate duration inputs."""
        try:
            min_val = int(self.min_duration_var.get()) if self.min_duration_var.get() else 0
            max_val = int(self.max_duration_var.get()) if self.max_duration_var.get() else 3600
            
            if min_val < 0:
                self.min_duration_var.set("0")
            if max_val < min_val:
                self.max_duration_var.set(str(min_val + 60))
        except ValueError:
            pass
    
    def _on_search_clicked(self) -> None:
        """Handle search button click."""
        if self.is_searching:
            return
        
        # Validate inputs
        if not self.search_entry.get().strip():
            tk.messagebox.showwarning("Search Error", "Please enter search keywords.")
            return
        
        # Build search configuration
        config = self._build_search_config()
        
        # Call callback if provided
        if self.on_search_clicked:
            self.is_searching = True
            self._update_search_state(True)
            self.on_search_clicked(config)
    
    def _build_search_config(self) -> SearchConfig:
        """Build SearchConfig object from current UI state."""
        # Map UI values to internal values
        sort_mapping = {
            "Relevance": "relevance",
            "Upload Date": "upload_date", 
            "View Count": "view_count",
            "Rating": "rating"
        }
        
        upload_date_mapping = {
            "Any Time": "any",
            "Past Hour": "hour",
            "Today": "today",
            "This Week": "week",
            "This Month": "month",
            "This Year": "year"
        }
        
        # Create filter config
        filter_config = FilterConfig(
            min_duration=int(self.min_duration_var.get()) if self.min_duration_var.get() else None,
            max_duration=int(self.max_duration_var.get()) if self.max_duration_var.get() else None,
            min_quality=self.min_quality_combo.get() if self.min_quality_combo.get() != "Any" else None,
            exclude_shorts=self.exclude_shorts_var.get(),
            exclude_live=self.exclude_live_var.get()
        )
        
        # Create search config
        config = SearchConfig(
            search_query=self.search_entry.get().strip(),
            max_results=int(self.quantity_var.get()),
            sort_by=sort_mapping.get(self.sort_combo.get(), "relevance"),
            upload_date=upload_date_mapping.get(self.upload_date_combo.get(), "any"),
            filter_config=filter_config
        )
        
        return config
    
    def _update_search_state(self, searching: bool) -> None:
        """Update UI elements based on search state."""
        self.is_searching = searching
        
        if searching:
            self.search_button.configure(
                text="🔄 Searching...",
                state="disabled"
            )
        else:
            self.search_button.configure(
                text="🔍 Search & Queue Downloads",
                state="normal"
            )
    
    def search_completed(self) -> None:
        """Called when search operation is completed."""
        self._update_search_state(False)
    
    def get_search_config(self) -> SearchConfig:
        """Get current search configuration."""
        return self._build_search_config()
    
    def reset(self) -> None:
        """Reset the search panel to default state."""
        self.search_entry.delete(0, tk.END)
        self.quantity_var.set("10")
        self.sort_combo.set("Relevance")
        self.min_duration_var.set("0")
        self.max_duration_var.set("3600")
        self.upload_date_combo.set("Any Time")
        self.exclude_shorts_var.set(True)
        self.exclude_live_var.set(True)
        self.min_quality_combo.set("Any")
        self.show_advanced.set(False)
        self._toggle_advanced_options()
        self.search_completed() 