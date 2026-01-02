import argparse
import sys
import logging
import os
import re
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path so we can import src
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.jina_client import fetch_markdown
from src.utils.llm_client import categorize_article, VALID_CATEGORIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def slugify(text: str) -> str:
    """
    Convert text to a filesystem-safe slug.
    Example: "Claude 3.5 Sonnet Released!" -> "claude-3-5-sonnet-released"
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # Remove special chars
    text = re.sub(r'\s+', '-', text)          # Replace spaces with hyphens
    return text.strip('-')

def save_article(url: str, content: str, metadata: dict, output_root: str = "data") -> str:
    """
    Save article to disk with frontmatter.
    
    Returns:
        Path to the saved file
    """
    category = metadata['category']
    title = metadata['title']
    summary = metadata['summary']
    today = date.today().isoformat()
    
    # Ensure category directory exists
    category_dir = Path(output_root) / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename
    safe_title = slugify(title)
    filename = f"{today}_{safe_title}.md"
    file_path = category_dir / filename
    
    # Construct file content with frontmatter
    file_content = f"""---
title: "{title}"
url: "{url}"
date: {today}
category: {category}
summary: "{summary}"
---

# {title}

{content}
"""
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
        
    return str(file_path)

def ingest_url(url: str, output_root: str = "data", category_hint: Optional[str] = None) -> None:
    """
    Main orchestration function to ingest a single URL.
    """
    logger.info(f"Starting ingestion for: {url}")
    
    try:
        # 1. Fetch content
        markdown_content = fetch_markdown(url)
        if not markdown_content:
            logger.error("Received empty content from Jina Reader")
            return

        # 2. Analyze with LLM
        metadata = categorize_article(markdown_content)
        
        # If we have a hint and the AI didn't find one (or we want to override), 
        # we can use the hint here. For now, we'll just log it.
        if category_hint:
            logger.info(f"Source hinted category: {category_hint}")
            
        logger.info(f"Categorized as: {metadata['category']}")
        
        # 3. Save to disk
        saved_path = save_article(url, markdown_content, metadata, output_root)
        logger.info(f"Successfully saved article to: {saved_path}")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Ingest a technical article from a URL.")
    parser.add_argument("url", help="URL of the article to ingest")
    parser.add_argument("--data-dir", default="data", help="Root directory for storing data")
    
    args = parser.parse_args()
    
    ingest_url(args.url, output_root=args.data_dir)

if __name__ == "__main__":
    main()
