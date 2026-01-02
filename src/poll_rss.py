import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Set
import feedparser
import yaml
from dateutil import parser as date_parser

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingest import ingest_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_sources(sources_path: str = "sources.json") -> List[dict]:
    with open(sources_path, 'r') as f:
        data = json.load(f)
    return data.get("feeds", [])

def get_ingested_urls(data_dir: str = "data") -> Set[str]:
    """
    Scan all markdown files in data_dir to find already ingested URLs.
    Returns a set of normalized URLs.
    """
    ingested = set()
    root = Path(data_dir)
    
    if not root.exists():
        return ingested
        
    for md_file in root.rglob("*.md"):
        try:
            # Quick and dirty frontmatter parse
            # We only read the first few lines to find 'url: "..."'
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read(1000) # Read first 1kb only
                
            # Parse yaml frontmatter if possible, or regex
            # Let's use basic regex for speed and robustness against malformed yaml
            match = re.search(r'^url:\s*["\']?([^"\']+)["\']?', content, re.MULTILINE)
            if match:
                ingested.add(match.group(1).strip())
        except Exception as e:
            logger.warning(f"Error reading {md_file}: {e}")
            
    return ingested

import re

def is_recent(entry, hours: int) -> bool:
    """Check if feed entry was published within the last N hours."""
    now = datetime.now().astimezone()
    published_time = None

    # Try different date fields
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed)).astimezone()
    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        published_time = datetime.fromtimestamp(time.mktime(entry.updated_parsed)).astimezone()
    
    if not published_time:
        # Fallback to string parsing if needed (removed for now to rely on feedparser)
        return False
        
    cutoff = now - timedelta(hours=hours)
    return published_time > cutoff

def poll_feeds(sources_path: str, data_dir: str, hours: int):
    feeds = load_sources(sources_path)
    existing_urls = get_ingested_urls(data_dir)
    
    logger.info(f"Found {len(existing_urls)} already ingested articles.")
    
    new_articles_count = 0
    
    for feed_cfg in feeds:
        url = feed_cfg['url']
        name = feed_cfg['name']
        logger.info(f"Checking feed: {name} ({url})")
        
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                link = entry.link.strip()
                
                # Check 1: Is it recent?
                if not is_recent(entry, hours):
                    continue
                    
                # Check 2: already ingested?
                if link in existing_urls:
                    continue
                    
                # Ingest
                logger.info(f"Found new article: {entry.title}")
                try:
                    category_hint = feed_cfg.get('default_category')
                    ingest_url(link, output_root=data_dir, category_hint=category_hint)
                    existing_urls.add(link)
                    new_articles_count += 1
                except Exception as e:
                    logger.error(f"Failed to ingest {link}: {e}")
                    
        except Exception as e:
            logger.error(f"Error parsing feed {name}: {e}")

    logger.info(f"Polling complete. Ingested {new_articles_count} new articles.")

def main():
    parser = argparse.ArgumentParser(description="Poll RSS feeds for new content.")
    parser.add_argument("--sources", default="sources.json", help="Path to sources.json")
    parser.add_argument("--data-dir", default="data", help="Root directory for data")
    parser.add_argument("--hours", type=int, default=24, help="Lookback window in hours")
    
    args = parser.parse_args()
    
    poll_feeds(args.sources, args.data_dir, args.hours)

if __name__ == "__main__":
    main()
