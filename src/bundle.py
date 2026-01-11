import argparse
import logging
import os
import re
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_frontmatter_value(content: str, key: str) -> str:
    """Extract value from key: value line in yaml frontmatter."""
    match = re.search(f'^{key}:\\s*["\']?([^"\']+)["\']?', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"

def bundle_category(category_path: Path, days: int, output_dir: Path):
    """
    Bundle recent files in a category directory into a digest.
    """
    category = category_path.name
    cutoff = datetime.now() - timedelta(days=days)
    
    # Find relevant files
    files_to_bundle = []
    
    if not category_path.exists():
        logger.warning(f"Category directory not found: {category_path}")
        return

    for md_file in category_path.glob("*.md"):
        # Check date in filename YYYY-MM-DD_...
        try:
            date_str = md_file.name[:10]
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if file_date > cutoff:
                files_to_bundle.append(md_file)
        except ValueError:
            logger.warning(f"Skipping file with invalid date format: {md_file.name}")
            continue
            
    if not files_to_bundle:
        logger.info(f"No recent files found for category: {category}")
        return
        
    logger.info(f"Bundling {len(files_to_bundle)} files for {category}...")
    
    # Sort by date (newest first)
    files_to_bundle.sort(key=lambda x: x.name, reverse=True)
    
    # Create valid filename
    today_str = date.today().isoformat()
    digest_filename = f"Weekly_Digest_{category}_{today_str}.md"

    # Create date-based subfolder
    date_folder = output_dir / today_str
    date_folder.mkdir(parents=True, exist_ok=True)
    digest_path = date_folder / digest_filename

    # Build Content
    toc_lines = []
    content_blocks = []
    url_list = []
    
    for i, file_path in enumerate(files_to_bundle):
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        # Parse simplified
        title = get_frontmatter_value(raw_content, "title")
        url = get_frontmatter_value(raw_content, "url")
        summary = get_frontmatter_value(raw_content, "summary")
        url_list.append(url)

        # Remove frontmatter for inclusion
        # Assume frontmatter ends at second ---
        parts = raw_content.split('---', 2)
        body = parts[2].strip() if len(parts) > 2 else raw_content
        
        anchor = f"article-{i}"
        toc_lines.append(f"{i+1}. [{title}](#{anchor})")
        
        block = f"""
---
<a id="{anchor}"></a>
## {title}
**Source:** {url}  
**Summary:** {summary}

{body}
"""
        content_blocks.append(block)

    # Assemble Final Markdown
    sources_section = "## Sources\n" + "\n".join(f"- {url}" for url in url_list)

    full_content = f"""# Weekly Digest: {category} - {today_str}

## Table of Contents
{chr(10).join(toc_lines)}

{sources_section}

{chr(10).join(content_blocks)}
"""

    with open(digest_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
        
    logger.info(f"Created digest: {digest_path}")

def main():
    parser = argparse.ArgumentParser(description="Bundle recent articles into digests.")
    parser.add_argument("--days", type=int, default=7, help="Include articles from last N days")
    parser.add_argument("--category", help="Specific category to bundle (default: all)")
    parser.add_argument("--data-dir", default="data", help="Root data directory")
    parser.add_argument("--output-dir", default="Digests", help="Output directory for digests")
    
    args = parser.parse_args()
    
    data_root = Path(args.data_dir)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    
    if args.category:
        # Bundle specific category
        bundle_category(data_root / args.category, args.days, output_root)
    else:
        # Bundle all found categories
        if data_root.exists():
            for cat_dir in data_root.iterdir():
                if cat_dir.is_dir():
                    bundle_category(cat_dir, args.days, output_root)
        else:
            logger.error(f"Data directory not found: {data_root}")

if __name__ == "__main__":
    main()
