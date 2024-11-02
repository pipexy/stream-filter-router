"""
Extract query parameters from a URL.
"""

from urllib.parse import urlparse, parse_qs

def extract_query_params(url: str) -> dict:
    """Extract query parameters from a URL."""
    parsed = urlparse(url)
    return {k: v[0] for k, v in parse_qs(parsed.query).items()}
