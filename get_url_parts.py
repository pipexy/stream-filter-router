"""
Extract scheme and base path from URL without query parameters.
"""

from urllib.parse import urlparse
import logging

def get_url_parts(url: str) -> tuple:
    """Get scheme and base path from URL without query parameters."""
    logger = logging.getLogger("StreamFilterRouter")
    
    # Handle simple scheme strings (like 'rtsp', 'hls', etc.)
    if '://' not in url:
        logger.debug(f"Parsing simple scheme {url}")
        return url, ''
            
    parsed = urlparse(url)
        
    # Handle process:// URLs specially to preserve the process name
    if parsed.scheme == 'process':
        # Extract process name from path or netloc
        process_name = parsed.path.strip('/').split('?')[0] or parsed.netloc.split('?')[0]
        logger.debug(f"Parsing process URL {url} -> scheme: process, path: {process_name}")
        return parsed.scheme, process_name
        
    # For other URLs, just return the scheme
    logger.debug(f"Parsing URL {url} -> scheme: {parsed.scheme}")
    return parsed.scheme, ''
