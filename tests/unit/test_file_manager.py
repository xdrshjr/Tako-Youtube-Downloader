"""
Unit tests for FileManager module.

Tests the file management functionality including file naming, path handling,
conflict resolution, and security validation.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from youtube_downloader.utils.file_manager import FileManager, FileConflictStrategy, SecurityError


class TestFileManager:
    """Test FileManager class functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.file_manager = FileManager(base_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_manager_initialization(self):
        """Test FileManager initialization."""
        manager = FileManager()
        assert manager.base_path == Path.cwd()
        
        manager = FileManager(base_path="/custom/path")
        # On Windows, resolve() converts paths to absolute with drive letter
        expected_path = Path("/custom/path").resolve()
        assert manager.base_path == expected_path
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test invalid characters
        assert self.file_manager.sanitize_filename("file<>name") == "file__name"
        assert self.file_manager.sanitize_filename("file:name") == "file_name"
        assert self.file_manager.sanitize_filename("file|name") == "file_name"
        assert self.file_manager.sanitize_filename("file?name") == "file_name"
        assert self.file_manager.sanitize_filename("file*name") == "file_name"
        
        # Test reserved names
        assert self.file_manager.sanitize_filename("CON") == "CON_"
        assert self.file_manager.sanitize_filename("PRN") == "PRN_"
        assert self.file_manager.sanitize_filename("AUX") == "AUX_"
        assert self.file_manager.sanitize_filename("NUL") == "NUL_"
        
        # Test length limit
        long_name = "a" * 300
        sanitized = self.file_manager.sanitize_filename(long_name)
        assert len(sanitized) <= 255
        
        # Test empty filename
        assert self.file_manager.sanitize_filename("") == "untitled"
        assert self.file_manager.sanitize_filename("   ") == "untitled"
    
    def test_validate_path_security(self):
        """Test path security validation."""
        # Test directory traversal attempts
        with pytest.raises(SecurityError):
            self.file_manager.validate_path("../../../etc/passwd")
        
        with pytest.raises(SecurityError):
            self.file_manager.validate_path("..\\..\\windows\\system32")
        
        with pytest.raises(SecurityError):
            self.file_manager.validate_path("/etc/passwd")
        
        # Test valid paths
        valid_path = self.file_manager.validate_path("subdir/file.txt")
        assert valid_path.is_relative_to(self.file_manager.base_path)
        
        valid_path = self.file_manager.validate_path("file.txt")
        assert valid_path.is_relative_to(self.file_manager.base_path)
    
    def test_build_output_path(self):
        """Test output path building."""
        video_info = {
            'title': 'Test Video',
            'id': 'TEST123',
            'uploader': 'Test Channel',
            'upload_date': '20240101'
        }
        
        # Test default pattern
        path = self.file_manager.build_output_path(
            pattern="{title}-{id}.{ext}",
            video_info=video_info,
            extension="mp4"
        )
        
        expected = self.temp_dir / "Test Video-TEST123.mp4"
        # Compare resolved paths to handle Windows short/long path differences
        assert path.resolve() == expected.resolve()
    
    def test_build_output_path_with_sanitization(self):
        """Test output path building with filename sanitization."""
        video_info = {
            'title': 'Test<>Video|?*',
            'id': 'TEST123',
            'uploader': 'Test Channel',
            'upload_date': '20240101'
        }
        
        path = self.file_manager.build_output_path(
            pattern="{title}-{id}.{ext}",
            video_info=video_info,
            extension="mp4"
        )
        
        # Title should be sanitized
        expected = self.temp_dir / "Test__Video___-TEST123.mp4"
        # Compare resolved paths to handle Windows short/long path differences
        assert path.resolve() == expected.resolve()
    
    def test_resolve_file_conflict_overwrite(self):
        """Test file conflict resolution with overwrite strategy."""
        # Create existing file
        existing_file = Path(self.temp_dir) / "test.mp4"
        existing_file.write_text("existing content")
        
        resolved_path = self.file_manager.resolve_file_conflict(
            target_path=existing_file,
            strategy=FileConflictStrategy.OVERWRITE
        )
        
        assert resolved_path == existing_file
    
    def test_resolve_file_conflict_skip(self):
        """Test file conflict resolution with skip strategy."""
        # Create existing file
        existing_file = Path(self.temp_dir) / "test.mp4"
        existing_file.write_text("existing content")
        
        resolved_path = self.file_manager.resolve_file_conflict(
            target_path=existing_file,
            strategy=FileConflictStrategy.SKIP
        )
        
        assert resolved_path is None
    
    def test_resolve_file_conflict_rename(self):
        """Test file conflict resolution with rename strategy."""
        # Create existing file
        existing_file = Path(self.temp_dir) / "test.mp4"
        existing_file.write_text("existing content")
        
        resolved_path = self.file_manager.resolve_file_conflict(
            target_path=existing_file,
            strategy=FileConflictStrategy.RENAME
        )
        
        assert resolved_path != existing_file
        assert resolved_path.stem == "test (1)"
        assert resolved_path.suffix == ".mp4"
    
    def test_resolve_file_conflict_rename_multiple(self):
        """Test file conflict resolution with multiple existing files."""
        # Create multiple existing files
        base_file = Path(self.temp_dir) / "test.mp4"
        base_file.write_text("content")
        
        file1 = Path(self.temp_dir) / "test (1).mp4"
        file1.write_text("content")
        
        file2 = Path(self.temp_dir) / "test (2).mp4"
        file2.write_text("content")
        
        resolved_path = self.file_manager.resolve_file_conflict(
            target_path=base_file,
            strategy=FileConflictStrategy.RENAME
        )
        
        assert resolved_path.stem == "test (3)"
        assert resolved_path.suffix == ".mp4"
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        target_dir = Path(self.temp_dir) / "subdir" / "nested"
        
        self.file_manager.ensure_directory_exists(target_dir)
        
        assert target_dir.exists()
        assert target_dir.is_dir()
    
    def test_check_disk_space(self):
        """Test disk space checking."""
        # Test with small required space (should pass)
        assert self.file_manager.check_disk_space(1024, self.temp_dir)
        
        # Test with very large required space (should fail)
        assert not self.file_manager.check_disk_space(999999999999999, self.temp_dir)
    
    def test_get_safe_filename_with_extension(self):
        """Test getting safe filename with proper extension handling."""
        filename = self.file_manager.get_safe_filename(
            "Test Video.mp4",
            fallback_extension="mkv"
        )
        
        assert filename == "Test Video.mp4"
        
        # Test without extension
        filename = self.file_manager.get_safe_filename(
            "Test Video",
            fallback_extension="mp4"
        )
        
        assert filename == "Test Video.mp4"
    
    def test_create_subdirectory_from_pattern(self):
        """Test creating subdirectories based on patterns."""
        video_info = {
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'upload_date': '20240101'
        }
        
        subdir = self.file_manager.create_subdirectory(
            pattern="{uploader}/{upload_date}",
            video_info=video_info
        )
        
        expected = self.temp_dir / "Test Channel" / "20240101"
        # Compare resolved paths to handle Windows short/long path differences
        assert subdir.resolve() == expected.resolve()
        assert subdir.exists()
        assert subdir.is_dir()
    
    def test_atomic_file_operation(self):
        """Test atomic file operations."""
        target_file = Path(self.temp_dir) / "atomic_test.txt"
        test_content = "Test content for atomic operation"
        
        with self.file_manager.atomic_write(target_file) as temp_file:
            temp_file.write_text(test_content)
        
        # Check that target file exists and has correct content
        assert target_file.exists()
        assert target_file.read_text() == test_content
    
    def test_atomic_file_operation_failure(self):
        """Test atomic file operation cleanup on failure."""
        target_file = Path(self.temp_dir) / "atomic_fail_test.txt"
        
        try:
            with self.file_manager.atomic_write(target_file) as temp_file:
                temp_file.write_text("Partial content")
                raise ValueError("Simulated failure")
        except ValueError:
            pass
        
        # Target file should not exist after failure
        assert not target_file.exists()
    
    def test_cleanup_temp_files(self):
        """Test cleanup of temporary files."""
        # Create some temporary files
        temp_file1 = Path(self.temp_dir) / "temp1.tmp"
        temp_file2 = Path(self.temp_dir) / "temp2.part"
        regular_file = Path(self.temp_dir) / "regular.mp4"
        
        temp_file1.write_text("temp content")
        temp_file2.write_text("temp content")
        regular_file.write_text("regular content")
        
        self.file_manager.cleanup_temp_files(self.temp_dir)
        
        # Temp files should be removed, regular file should remain
        assert not temp_file1.exists()
        assert not temp_file2.exists()
        assert regular_file.exists()
    
    def test_file_metadata_extraction(self):
        """Test extracting file metadata."""
        test_file = Path(self.temp_dir) / "test.mp4"
        test_content = "Test video content"
        test_file.write_text(test_content)
        
        metadata = self.file_manager.get_file_metadata(test_file)
        
        assert metadata['size'] == len(test_content)
        assert metadata['path'] == str(test_file)
        assert 'created_time' in metadata
        assert 'modified_time' in metadata
    
    def test_validate_write_permissions(self):
        """Test write permission validation."""
        # Test with valid directory
        assert self.file_manager.validate_write_permissions(self.temp_dir)
        
        # Test with non-existent parent directory
        non_existent = Path(self.temp_dir) / "non_existent" / "deep" / "path"
        assert self.file_manager.validate_write_permissions(non_existent.parent)


class TestFileConflictStrategy:
    """Test FileConflictStrategy enum."""
    
    def test_strategy_values(self):
        """Test strategy enum values."""
        assert FileConflictStrategy.OVERWRITE.value == "overwrite"
        assert FileConflictStrategy.SKIP.value == "skip"
        assert FileConflictStrategy.RENAME.value == "rename"
        assert FileConflictStrategy.ASK.value == "ask"


class TestSecurityError:
    """Test SecurityError exception."""
    
    def test_security_error_creation(self):
        """Test SecurityError exception creation."""
        error = SecurityError("Test security error")
        assert str(error) == "Test security error"
        assert isinstance(error, Exception) 