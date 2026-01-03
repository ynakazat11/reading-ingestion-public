import requests
import logging
import os
import time
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


def fetch_markdown(
    url: str,
    api_key: Optional[str] = None,
    max_retries: int = 3,
    initial_timeout: int = 45
) -> str:
    """
    Fetch URL content as Markdown via Jina Reader with retry logic.
    
    Args:
        url: The article URL to convert.
        api_key: Optional Jina API key for higher rate limits.
        max_retries: Maximum number of retry attempts (default: 3).
        initial_timeout: Initial timeout in seconds, increases with each retry.
        
    Returns:
        Markdown string of the article content.
        
    Raises:
        requests.RequestException: If all retry attempts fail.
    """
    jina_url = f"https://r.jina.ai/{url}"
    headers = {}
    
    # Check for API key in args or environment
    key = api_key or os.getenv("JINA_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
        
    logger.info(f"Fetching content from Jina Reader for: {url}")
    
    last_error = None
    for attempt in range(max_retries):
        # Increase timeout with each retry (45s, 60s, 90s)
        timeout = initial_timeout + (attempt * 15)
        
        try:
            if attempt > 0:
                # Exponential backoff: 2s, 4s, 8s...
                wait_time = 2 ** attempt
                logger.info(f"Retry {attempt}/{max_retries-1} after {wait_time}s wait (timeout: {timeout}s)")
                time.sleep(wait_time)
            
            response = requests.get(jina_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            if attempt > 0:
                logger.info(f"Successfully fetched on retry {attempt}")
            
            return response.text
            
        except requests.exceptions.Timeout as e:
            last_error = e
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}: {e}")
            
        except requests.exceptions.RequestException as e:
            # For non-timeout errors, don't retry
            logger.error(f"Failed to fetch content from Jina Reader: {e}")
            raise
    
    # All retries exhausted
    logger.error(f"All {max_retries} attempts failed for {url}")
    raise requests.exceptions.Timeout(
        f"Failed after {max_retries} attempts: {last_error}"
    )
