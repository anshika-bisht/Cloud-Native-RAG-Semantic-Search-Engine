import re
from fastapi import HTTPException

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes user-uploaded filenames to prevent path traversal and shell injection.
    """
    # Keep only alphanumeric, dashes, dots, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
    if not sanitized or sanitized.startswith('.'):
        sanitized = "unnamed_file.pdf"
    return sanitized

def validate_file_size(file_size: int, max_size_mb: int) -> None:
    """
    Validates that the uploaded file does not exceed the maximum allowed size.
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=413, 
            detail=f"File exceeds maximum allowed size of {max_size_mb} MB."
        )
