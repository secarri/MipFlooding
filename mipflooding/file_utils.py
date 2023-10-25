# Default packages
from pathlib import Path


def clear_log_file(filepath: str) -> None:
    """Clear the content of the log file at the specified 'filepath' if it exists."""
    if Path(filepath).exists():
        with open(filepath, 'w') as f:
            pass


def get_output_directory(filepath: str) -> str | None:
    """Get the parent directory of the specified 'filepath' as a string if it exists, or return None."""
    parent_path = Path(filepath).parent
    return parent_path.__str__() if parent_path.exists() else None


def get_output_filename(filepath: str) -> str | None:
    """Get the filename from the specified 'filepath' as a string, or return None if the path is empty."""
    return Path(filepath).name.__str__()
