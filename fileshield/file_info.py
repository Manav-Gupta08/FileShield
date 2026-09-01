"""File information extraction module."""

import os
from pathlib import Path
from datetime import datetime


class FileInformation:
    """Extract and format basic file information."""

    def __init__(self, file_path: str):
        """
        Initialize with a file path.

        Args:
            file_path: Path to the file to analyze

        Raises:
            FileNotFoundError: If file does not exist
            IsADirectoryError: If path points to a directory
        """
        self.path = Path(file_path)

        # Validate that the path exists and is a file
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.path.is_dir():
            raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")

    def get_info(self) -> dict:
        """
        Extract file information.

        Returns:
            Dictionary containing file metadata
        """
        stat = self.path.stat()

        return {
            "filename": self.path.name,
            "absolute_path": str(self.path.absolute()),
            "size_bytes": stat.st_size,
            "extension": self.path.suffix.lower() if self.path.suffix else "(no extension)",
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "readable": os.access(self.path, os.R_OK),
            "writable": os.access(self.path, os.W_OK),
        }

    def format_size(self, size_bytes: int) -> str:
        """
        Convert bytes to human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def display(self) -> None:
        """Print formatted file information to console."""
        info = self.get_info()

        print("\n" + "=" * 60)
        print("FILE INFORMATION")
        print("=" * 60)
        print(f"Filename:        {info['filename']}")
        print(f"Path:            {info['absolute_path']}")
        print(f"Size:            {self.format_size(info['size_bytes'])} ({info['size_bytes']:,} bytes)")
        print(f"Extension:       {info['extension']}")
        print(f"Created:         {info['created_time']}")
        print(f"Modified:        {info['modified_time']}")
        print(f"Accessed:        {info['accessed_time']}")
        print(f"Readable:        {'Yes' if info['readable'] else 'No'}")
        print(f"Writable:        {'Yes' if info['writable'] else 'No'}")
        print("=" * 60 + "\n")
