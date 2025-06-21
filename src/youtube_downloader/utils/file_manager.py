"""
File management module for YouTube Downloader.

This module provides secure file operations, naming conventions,
conflict resolution, and path validation.
"""

import os
import re
import shutil
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from contextlib import contextmanager
import stat
import time


class FileConflictStrategy(Enum):
    """File conflict resolution strategies."""
    OVERWRITE = "overwrite"
    SKIP = "skip"
    RENAME = "rename"
    ASK = "ask"


class SecurityError(Exception):
    """Exception raised for security-related file operations."""
    pass


class FileManager:
    """
    Secure file manager with path validation and conflict resolution.
    
    Features:
    - Path security validation (prevent directory traversal)
    - Filename sanitization
    - File conflict resolution
    - Atomic file operations
    - Disk space checking
    - Pattern-based path building
    """
    
    # Invalid filename characters (Windows + Unix)
    INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1f]'
    
    # Reserved filenames (Windows)
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    # Temporary file extensions to clean up
    TEMP_EXTENSIONS = {'.tmp', '.part', '.temp', '.download'}
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize file manager.
        
        Args:
            base_path: Base directory for file operations (defaults to cwd)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.base_path = self.base_path.resolve()
    
    def sanitize_filename(self, filename: str, max_length: int = 255) -> str:
        """
        Sanitize filename to be safe for filesystem.
        
        Args:
            filename: Original filename
            max_length: Maximum filename length
            
        Returns:
            Sanitized filename
        """
        if not filename or filename.isspace():
            return "untitled"
        
        # Remove invalid characters
        sanitized = re.sub(self.INVALID_CHARS, '_', filename)
        
        # Handle reserved names
        name_without_ext = Path(sanitized).stem.upper()
        if name_without_ext in self.RESERVED_NAMES:
            sanitized = sanitized + '_'
        
        # Trim length while preserving extension
        if len(sanitized) > max_length:
            path_obj = Path(sanitized)
            stem = path_obj.stem
            suffix = path_obj.suffix
            
            # Calculate available space for stem
            available_length = max_length - len(suffix)
            if available_length > 0:
                sanitized = stem[:available_length] + suffix
            else:
                sanitized = stem[:max_length]
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        return sanitized or "untitled"
    
    def validate_path(self, path: Union[str, Path]) -> Path:
        """
        Validate path for security (prevent directory traversal).
        
        Args:
            path: Path to validate
            
        Returns:
            Validated absolute path
            
        Raises:
            SecurityError: If path is unsafe
        """
        path_obj = Path(path)
        
        # Convert to absolute path relative to base_path
        if path_obj.is_absolute():
            # Absolute paths are not allowed for security
            raise SecurityError(f"Absolute paths are not allowed: {path}")
        
        # Resolve the path relative to base_path
        resolved_path = (self.base_path / path_obj).resolve()
        
        # Check if resolved path is within base_path
        try:
            resolved_path.relative_to(self.base_path)
        except ValueError:
            raise SecurityError(f"Path traversal attempt detected: {path}")
        
        return resolved_path
    
    def build_output_path(
        self,
        pattern: str,
        video_info: Dict[str, Any],
        extension: str,
        subdirectory: Optional[str] = None
    ) -> Path:
        """
        Build output path using pattern and video information.
        
        Args:
            pattern: Naming pattern (e.g., "{title}-{id}.{ext}")
            video_info: Video metadata dictionary
            extension: File extension
            subdirectory: Optional subdirectory pattern
            
        Returns:
            Complete output path
        """
        # Create a copy of video_info for formatting
        format_dict = video_info.copy()
        format_dict['ext'] = extension
        
        # Sanitize all string values in format_dict
        for key, value in format_dict.items():
            if isinstance(value, str):
                format_dict[key] = self.sanitize_filename(value)
        
        # Format the filename
        try:
            filename = pattern.format(**format_dict)
        except KeyError as e:
            raise ValueError(f"Missing key in pattern: {e}")
        
        # Sanitize the final filename
        filename = self.sanitize_filename(filename)
        
        # Build the full path
        if subdirectory:
            subdir_path = self.create_subdirectory(subdirectory, video_info)
            full_path = subdir_path / filename
        else:
            full_path = self.base_path / filename
        
        return full_path
    
    def create_subdirectory(self, pattern: str, video_info: Dict[str, Any]) -> Path:
        """
        Create subdirectory based on pattern.
        
        Args:
            pattern: Directory pattern (e.g., "{uploader}/{upload_date}")
            video_info: Video metadata dictionary
            
        Returns:
            Created subdirectory path
        """
        # Create format dictionary with sanitized values
        format_dict = {}
        for key, value in video_info.items():
            if isinstance(value, str):
                format_dict[key] = self.sanitize_filename(value)
            else:
                format_dict[key] = value
        
        # Format the subdirectory path
        try:
            subdir_str = pattern.format(**format_dict)
        except KeyError as e:
            raise ValueError(f"Missing key in subdirectory pattern: {e}")
        
        # Sanitize each path component
        parts = []
        for part in subdir_str.split('/'):
            if part:  # Skip empty parts
                parts.append(self.sanitize_filename(part))
        
        # Build the subdirectory path
        subdir_path = self.base_path
        for part in parts:
            subdir_path = subdir_path / part
        
        # Create the directory
        self.ensure_directory_exists(subdir_path)
        
        return subdir_path
    
    def resolve_file_conflict(
        self,
        target_path: Path,
        strategy: FileConflictStrategy = FileConflictStrategy.RENAME
    ) -> Optional[Path]:
        """
        Resolve file conflict using specified strategy.
        
        Args:
            target_path: Target file path
            strategy: Conflict resolution strategy
            
        Returns:
            Resolved path or None if skipped
        """
        if not target_path.exists():
            return target_path
        
        if strategy == FileConflictStrategy.OVERWRITE:
            return target_path
        
        elif strategy == FileConflictStrategy.SKIP:
            return None
        
        elif strategy == FileConflictStrategy.RENAME:
            return self._find_available_name(target_path)
        
        elif strategy == FileConflictStrategy.ASK:
            # In automated context, default to rename
            return self._find_available_name(target_path)
        
        else:
            raise ValueError(f"Unknown conflict strategy: {strategy}")
    
    def _find_available_name(self, target_path: Path) -> Path:
        """
        Find available filename by appending numbers.
        
        Args:
            target_path: Original target path
            
        Returns:
            Available path with number suffix
        """
        counter = 1
        while True:
            stem = target_path.stem
            suffix = target_path.suffix
            parent = target_path.parent
            
            new_name = f"{stem} ({counter}){suffix}"
            new_path = parent / new_name
            
            if not new_path.exists():
                return new_path
            
            counter += 1
            
            # Prevent infinite loop
            if counter > 9999:
                raise RuntimeError("Could not find available filename")
    
    def ensure_directory_exists(self, directory: Path):
        """
        Ensure directory exists, creating it if necessary.
        
        Args:
            directory: Directory path to create
        """
        directory.mkdir(parents=True, exist_ok=True)
    
    def check_disk_space(self, required_bytes: int, path: Optional[Path] = None) -> bool:
        """
        Check if sufficient disk space is available.
        
        Args:
            required_bytes: Required space in bytes
            path: Path to check (defaults to base_path)
            
        Returns:
            True if sufficient space available
        """
        check_path = path or self.base_path
        
        try:
            # Get disk usage statistics
            if hasattr(shutil, 'disk_usage'):
                # Python 3.3+
                _, _, free_bytes = shutil.disk_usage(check_path)
            else:
                # Fallback for older Python versions
                stat_result = os.statvfs(check_path)
                free_bytes = stat_result.f_bavail * stat_result.f_frsize
            
            return free_bytes >= required_bytes
        except (OSError, AttributeError):
            # If we can't check, assume space is available
            return True
    
    def get_safe_filename(self, filename: str, fallback_extension: str = "") -> str:
        """
        Get safe filename with proper extension handling.
        
        Args:
            filename: Original filename
            fallback_extension: Extension to add if none present
            
        Returns:
            Safe filename with extension
        """
        safe_name = self.sanitize_filename(filename)
        
        # Add extension if not present
        if fallback_extension and not Path(safe_name).suffix:
            safe_name = f"{safe_name}.{fallback_extension.lstrip('.')}"
        
        return safe_name
    
    @contextmanager
    def atomic_write(self, target_path: Path):
        """
        Context manager for atomic file writing.
        
        Args:
            target_path: Final target path
            
        Yields:
            Temporary file path for writing
        """
        # Create temporary file in same directory as target
        temp_dir = target_path.parent
        self.ensure_directory_exists(temp_dir)
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(
            dir=temp_dir,
            prefix=f".{target_path.name}.",
            suffix=".tmp"
        )
        
        temp_path = Path(temp_path)
        
        try:
            # Close the file descriptor, we'll use Path methods
            os.close(temp_fd)
            
            yield temp_path
            
            # Move temporary file to final location
            temp_path.replace(target_path)
            
        except Exception:
            # Clean up temporary file on error
            try:
                temp_path.unlink()
            except OSError:
                pass
            raise

    def cleanup_temp_files(self, directory: Union[str, Path]):
        """
        Clean up temporary files in directory.

        Args:
            directory: Directory to clean
        """
        directory = Path(directory)
        if not directory.exists():
            return
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix in self.TEMP_EXTENSIONS:
                try:
                    file_path.unlink()
                except OSError:
                    # Ignore errors (file might be in use)
                    pass
    
    def get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Get file metadata.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat_info = file_path.stat()
        
        return {
            'path': str(file_path),
            'size': stat_info.st_size,
            'created_time': stat_info.st_ctime,
            'modified_time': stat_info.st_mtime,
            'is_file': file_path.is_file(),
            'is_directory': file_path.is_dir(),
            'permissions': oct(stat_info.st_mode)[-3:]
        }

    def validate_write_permissions(self, path: Union[str, Path]) -> bool:
        """
        Validate write permissions for path.

        Args:
            path: Path to check

        Returns:
            True if writable
        """
        path = Path(path)
        try:
            # Check if path exists
            if path.exists():
                return os.access(path, os.W_OK)
            
            # Check parent directory
            parent = path.parent
            while parent != parent.parent:  # Not root
                if parent.exists():
                    return os.access(parent, os.W_OK)
                parent = parent.parent
            
            return False
        except OSError:
            return False
    
    def move_file(self, source: Path, destination: Path, conflict_strategy: FileConflictStrategy = FileConflictStrategy.RENAME) -> Optional[Path]:
        """
        Move file with conflict resolution.
        
        Args:
            source: Source file path
            destination: Destination file path
            conflict_strategy: How to handle conflicts
            
        Returns:
            Final destination path or None if skipped
        """
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        # Resolve any conflicts
        final_dest = self.resolve_file_conflict(destination, conflict_strategy)
        if final_dest is None:
            return None
        
        # Ensure destination directory exists
        self.ensure_directory_exists(final_dest.parent)
        
        # Move the file
        shutil.move(str(source), str(final_dest))
        
        return final_dest
    
    def copy_file(self, source: Path, destination: Path, conflict_strategy: FileConflictStrategy = FileConflictStrategy.RENAME) -> Optional[Path]:
        """
        Copy file with conflict resolution.
        
        Args:
            source: Source file path
            destination: Destination file path
            conflict_strategy: How to handle conflicts
            
        Returns:
            Final destination path or None if skipped
        """
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        # Resolve any conflicts
        final_dest = self.resolve_file_conflict(destination, conflict_strategy)
        if final_dest is None:
            return None
        
        # Ensure destination directory exists
        self.ensure_directory_exists(final_dest.parent)
        
        # Copy the file
        shutil.copy2(str(source), str(final_dest))
        
        return final_dest 