"""
Convert file:/// URL to local path.
"""

def convert_file_path(url: str) -> str:
    """Convert file:/// URL to local path."""
    if url.startswith('file:///'):
        # Convert to relative path
        path = url[7:]  # Remove file:///
        if path.startswith('/'):
            path = '.' + path
        return path
    return url
