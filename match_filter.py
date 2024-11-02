"""
Match normalized chain against filter chain.
"""

import logging
from get_url_parts import get_url_parts

def match_filter(filter_chain: list[str], normalized_chain: list[str]) -> bool:
    """Match normalized chain against filter chain."""
    logger = logging.getLogger("StreamFilterRouter")
    logger.debug(f"Matching filter chain {filter_chain} against normalized chain {normalized_chain}")
        
    if len(filter_chain) != len(normalized_chain):
        logger.debug(f"Length mismatch: filter chain ({len(filter_chain)}) != normalized chain ({len(normalized_chain)})")
        return False

    for idx, (filter_url, norm_url) in enumerate(zip(filter_chain, normalized_chain)):
        logger.debug(f"Comparing position {idx}: filter '{filter_url}' vs normalized '{norm_url}'")
            
        filter_scheme, filter_path = get_url_parts(filter_url)
            
        if '://' in norm_url:
            # This is a process:// URL
            norm_scheme, norm_path = get_url_parts(norm_url)
            if filter_scheme != norm_scheme or filter_path != norm_path:
                logger.debug(f"Process URL mismatch at position {idx}")
                logger.debug(f"Filter: scheme={filter_scheme}, path={filter_path}")
                logger.debug(f"Norm: scheme={norm_scheme}, path={norm_path}")
                return False
        else:
            # This is just a scheme
            if filter_scheme != norm_url:
                logger.debug(f"Scheme mismatch at position {idx}: {filter_scheme} != {norm_url}")
                return False

    logger.debug("Filter chain matches normalized chain")
    return True
