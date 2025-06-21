"""
Unit tests for GUI components.

Tests the functionality of individual GUI components to ensure
they work correctly and follow the expected behavior patterns.
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Mock customtkinter before importing GUI components
sys.modules['customtkinter'] = MagicMock()

from youtube_downloader.gui.styles.themes import ThemeManager, AppTheme
from youtube_downloader.core.validator import URLValidator


class TestThemeManager(unittest.TestCase):
    """Test theme management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.theme_manager = ThemeManager()
    
    def test_default_theme(self):
        """Test default theme is dark."""
        self.assertEqual(self.theme_manager.theme_name, "dark")
        self.assertEqual(self.theme_manager.current_theme, AppTheme.DARK)
    
    def test_set_theme_dark(self):
        """Test setting dark theme."""
        self.theme_manager.set_theme("dark")
        self.assertEqual(self.theme_manager.theme_name, "dark")
        self.assertEqual(self.theme_manager.current_theme, AppTheme.DARK)
    
    def test_set_theme_light(self):
        """Test setting light theme."""
        self.theme_manager.set_theme("light")
        self.assertEqual(self.theme_manager.theme_name, "light")
        self.assertEqual(self.theme_manager.current_theme, AppTheme.LIGHT)
    
    def test_invalid_theme(self):
        """Test setting invalid theme raises error."""
        with self.assertRaises(ValueError):
            self.theme_manager.set_theme("invalid")
    
    def test_get_color(self):
        """Test getting color from theme."""
        color = self.theme_manager.get_color("primary")
        self.assertIsInstance(color, str)
        self.assertTrue(color.startswith("#"))
    
    def test_get_font(self):
        """Test getting font configuration."""
        font = self.theme_manager.get_font("heading")
        self.assertIsInstance(font, tuple)
        self.assertEqual(len(font), 3)
    
    def test_get_spacing(self):
        """Test getting spacing values."""
        spacing = self.theme_manager.get_spacing("md")
        self.assertIsInstance(spacing, int)
        self.assertGreater(spacing, 0)
    
    def test_get_dimension(self):
        """Test getting dimension values."""
        dimension = self.theme_manager.get_dimension("button_height")
        self.assertIsInstance(dimension, int)
        self.assertGreater(dimension, 0)


class TestURLValidation(unittest.TestCase):
    """Test URL validation for GUI input."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = URLValidator()
    
    def test_valid_youtube_urls(self):
        """Test valid YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.validator.validate_youtube_url(url))
    
    def test_invalid_urls(self):
        """Test invalid URLs."""
        invalid_urls = [
            "",
            "not_a_url",
            "https://www.google.com",
            "https://www.youtube.com",  # No video ID
            "https://vimeo.com/123456789"
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.validator.validate_youtube_url(url))
    
    def test_extract_video_id(self):
        """Test video ID extraction."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ")
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                video_id = self.validator.extract_video_id(url)
                self.assertEqual(video_id, expected_id)


class TestGUIComponentMocks(unittest.TestCase):
    """Test GUI component behavior with mocked dependencies."""
    
    def setUp(self):
        """Set up test mocks."""
        self.mock_parent = Mock()
        self.mock_callback = Mock()
    
    @patch('youtube_downloader.gui.components.url_input.URLValidator')
    def test_url_input_panel_creation(self, mock_validator_class):
        """Test URL input panel can be created."""
        # This test verifies the import structure works
        try:
            from youtube_downloader.gui.components.url_input import URLInputPanel
            # If we can import it, the structure is correct
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import URLInputPanel: {e}")
    
    def test_settings_panel_creation(self):
        """Test settings panel can be created."""
        try:
            from youtube_downloader.gui.components.settings_panel import SettingsPanel
            # If we can import it, the structure is correct
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import SettingsPanel: {e}")
    
    def test_progress_panel_creation(self):
        """Test progress panel can be created."""
        try:
            from youtube_downloader.gui.components.progress_panel import ProgressPanel
            # If we can import it, the structure is correct
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import ProgressPanel: {e}")
    
    def test_log_panel_creation(self):
        """Test log panel can be created."""
        try:
            from youtube_downloader.gui.components.log_panel import LogPanel
            # If we can import it, the structure is correct
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import LogPanel: {e}")
    
    def test_video_info_panel_creation(self):
        """Test video info panel can be created."""
        try:
            from youtube_downloader.gui.components.video_info_panel import VideoInfoPanel
            # If we can import it, the structure is correct
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import VideoInfoPanel: {e}")


class TestGUIIntegration(unittest.TestCase):
    """Test GUI component integration."""
    
    def test_theme_color_consistency(self):
        """Test that all themes have consistent color definitions."""
        required_colors = [
            'primary', 'primary_hover', 'primary_text',
            'secondary', 'secondary_hover', 'secondary_text',
            'bg_primary', 'bg_secondary', 'bg_tertiary',
            'text_primary', 'text_secondary', 'text_disabled',
            'success', 'warning', 'error', 'info',
            'border', 'accent'
        ]
        
        for theme in [AppTheme.DARK, AppTheme.LIGHT]:
            for color_name in required_colors:
                with self.subTest(theme=theme, color=color_name):
                    self.assertTrue(hasattr(theme, color_name))
                    color_value = getattr(theme, color_name)
                    self.assertIsInstance(color_value, str)
                    self.assertTrue(color_value.startswith("#"))
    
    def test_font_configuration(self):
        """Test font configuration completeness."""
        theme_manager = ThemeManager()
        required_fonts = ['heading', 'subheading', 'body', 'small', 'mono']
        
        for font_name in required_fonts:
            with self.subTest(font=font_name):
                font_config = theme_manager.get_font(font_name)
                self.assertIsInstance(font_config, tuple)
                self.assertEqual(len(font_config), 3)
                self.assertIsInstance(font_config[0], str)  # Font family
                self.assertIsInstance(font_config[1], int)  # Font size
                self.assertIsInstance(font_config[2], str)  # Font weight
    
    def test_spacing_configuration(self):
        """Test spacing configuration completeness."""
        theme_manager = ThemeManager()
        required_spacings = ['xs', 'sm', 'md', 'lg', 'xl']
        
        for spacing_name in required_spacings:
            with self.subTest(spacing=spacing_name):
                spacing_value = theme_manager.get_spacing(spacing_name)
                self.assertIsInstance(spacing_value, int)
                self.assertGreater(spacing_value, 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2) 