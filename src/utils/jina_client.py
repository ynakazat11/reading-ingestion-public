import requests
import logging
import os
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

def fetch_markdown(url: str, api_key: Optional[str] = None) -> str:
    """
    Fetch URL content as Markdown via Jina Reader.
    
    Args:
        url: The article URL to convert.
        api_key: Optional Jina API key for higher rate limits.
        
    Returns:
        Markdown string of the article content.
        
    Raises:
        requests.RequestException: If the request fails.
    """
    jina_url = f"https://r.jina.ai/{url}"
    headers = {}
    
    # Check for API key in args or environment
    key = api_key or os.getenv("JINA_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
        
    logger.info(f"Fetching content from Jina Reader for: {url}")
    
    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch content from Jina Reader: {e}")
        raise
