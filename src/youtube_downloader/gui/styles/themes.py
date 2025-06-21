"""
Theme and Style Configuration for YouTube Downloader GUI

Provides modern, elegant color schemes and styling constants following
Material Design principles and human-computer interaction best practices.
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import customtkinter as ctk


@dataclass
class ColorScheme:
    """Color scheme definition for UI themes."""
    
    # Primary colors
    primary: str
    primary_hover: str
    primary_text: str
    
    # Secondary colors
    secondary: str
    secondary_hover: str
    secondary_text: str
    
    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str
    
    # Status colors
    success: str
    warning: str
    error: str
    info: str
    
    # Border and accent colors
    border: str
    accent: str


class AppTheme:
    """Application theme definitions with modern color schemes."""
    
    # Dark theme (default)
    DARK = ColorScheme(
        # Primary colors - Modern blue
        primary="#1f6aa5",
        primary_hover="#2980b9",
        primary_text="#ffffff",
        
        # Secondary colors - Elegant gray
        secondary="#34495e",
        secondary_hover="#2c3e50",
        secondary_text="#ecf0f1",
        
        # Background colors - Dark theme
        bg_primary="#2b2b2b",
        bg_secondary="#212121",
        bg_tertiary="#1a1a1a",
        
        # Text colors - High contrast
        text_primary="#ffffff",
        text_secondary="#bdc3c7",
        text_disabled="#7f8c8d",
        
        # Status colors - Clear and accessible
        success="#27ae60",
        warning="#f39c12",
        error="#e74c3c",
        info="#3498db",
        
        # Border and accent
        border="#404040",
        accent="#8e44ad"  # TakoAI purple accent
    )
    
    # Light theme
    LIGHT = ColorScheme(
        # Primary colors - Professional blue
        primary="#2c3e50",
        primary_hover="#34495e",
        primary_text="#ffffff",
        
        # Secondary colors - Light gray
        secondary="#ecf0f1",
        secondary_hover="#d5dbdb",
        secondary_text="#2c3e50",
        
        # Background colors - Clean white/light
        bg_primary="#ffffff",
        bg_secondary="#f8f9fa",
        bg_tertiary="#ecf0f1",
        
        # Text colors - Dark on light
        text_primary="#2c3e50",
        text_secondary="#5d6d7e",
        text_disabled="#bdc3c7",
        
        # Status colors - Consistent with dark theme
        success="#27ae60",
        warning="#e67e22",
        error="#c0392b",
        info="#2980b9",
        
        # Border and accent
        border="#d5dbdb",
        accent="#8e44ad"
    )


class ThemeManager:
    """Manages application themes and styling."""
    
    def __init__(self):
        self.current_theme = AppTheme.DARK
        self.theme_name = "dark"
        
        # Font configurations
        self.fonts = {
            "heading": ("Segoe UI", 22, "bold"),
            "subheading": ("Segoe UI", 16, "bold"),
            "body": ("Segoe UI", 12, "normal"),
            "small": ("Segoe UI", 11, "normal"),
            "mono": ("Consolas", 10, "normal"),
            "logo": ("Segoe UI", 24, "bold"),
            "tagline": ("Segoe UI", 10, "normal")
        }
        
        # Spacing constants
        self.spacing = {
            "xs": 6,
            "sm": 12,
            "md": 20,
            "lg": 28,
            "xl": 36
        }
        
        # Component dimensions
        self.dimensions = {
            "button_height": 42,
            "input_height": 38,
            "panel_padding": 20,
            "border_radius": 8,
            "border_width": 1
        }
    
    def set_theme(self, theme_name: str) -> None:
        """
        Set the current theme.
        
        Args:
            theme_name: "dark" or "light"
        """
        if theme_name.lower() == "dark":
            self.current_theme = AppTheme.DARK
            self.theme_name = "dark"
            ctk.set_appearance_mode("dark")
        elif theme_name.lower() == "light":
            self.current_theme = AppTheme.LIGHT
            self.theme_name = "light"
            ctk.set_appearance_mode("light")
        else:
            raise ValueError(f"Unknown theme: {theme_name}")
    
    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme."""
        return getattr(self.current_theme, color_name)
    
    def get_font(self, font_name: str) -> Tuple[str, int, str]:
        """Get a font configuration."""
        return self.fonts.get(font_name, self.fonts["body"])
    
    def get_spacing(self, size: str) -> int:
        """Get spacing value."""
        return self.spacing.get(size, self.spacing["md"])
    
    def get_dimension(self, name: str) -> int:
        """Get dimension value."""
        return self.dimensions.get(name, 0)
    
    def configure_ctk_theme(self) -> None:
        """Configure CustomTkinter with current theme colors."""
        theme_colors = {
            "CTkToplevel": {
                "fg_color": [self.current_theme.bg_primary, self.current_theme.bg_primary]
            },
            "CTkFrame": {
                "fg_color": [self.current_theme.bg_secondary, self.current_theme.bg_secondary],
                "border_color": [self.current_theme.border, self.current_theme.border]
            },
            "CTkButton": {
                "fg_color": [self.current_theme.primary, self.current_theme.primary],
                "hover_color": [self.current_theme.primary_hover, self.current_theme.primary_hover],
                "text_color": [self.current_theme.primary_text, self.current_theme.primary_text],
                "border_color": [self.current_theme.border, self.current_theme.border]
            },
            "CTkEntry": {
                "fg_color": [self.current_theme.bg_tertiary, self.current_theme.bg_tertiary],
                "border_color": [self.current_theme.border, self.current_theme.border],
                "text_color": [self.current_theme.text_primary, self.current_theme.text_primary],
                "placeholder_text_color": [self.current_theme.text_disabled, self.current_theme.text_disabled]
            },
            "CTkTextbox": {
                "fg_color": [self.current_theme.bg_tertiary, self.current_theme.bg_tertiary],
                "border_color": [self.current_theme.border, self.current_theme.border],
                "text_color": [self.current_theme.text_primary, self.current_theme.text_primary]
            },
            "CTkScrollbar": {
                "fg_color": [self.current_theme.bg_secondary, self.current_theme.bg_secondary],
                "button_color": [self.current_theme.accent, self.current_theme.accent],
                "button_hover_color": [self.current_theme.primary_hover, self.current_theme.primary_hover]
            },
            "CTkProgressBar": {
                "fg_color": [self.current_theme.bg_tertiary, self.current_theme.bg_tertiary],
                "progress_color": [self.current_theme.primary, self.current_theme.primary],
                "border_color": [self.current_theme.border, self.current_theme.border]
            },
            "CTkComboBox": {
                "fg_color": [self.current_theme.bg_tertiary, self.current_theme.bg_tertiary],
                "border_color": [self.current_theme.border, self.current_theme.border],
                "button_color": [self.current_theme.secondary, self.current_theme.secondary],
                "button_hover_color": [self.current_theme.secondary_hover, self.current_theme.secondary_hover],
                "text_color": [self.current_theme.text_primary, self.current_theme.text_primary]
            }
        }
        
        # Apply the custom theme
        for widget_name, colors in theme_colors.items():
            try:
                ctk.ThemeManager.theme[widget_name].update(colors)
            except (KeyError, AttributeError):
                # Widget type might not exist in this version
                continue


# Global theme manager instance
theme_manager = ThemeManager() 