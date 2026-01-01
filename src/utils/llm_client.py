import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

# Valid categories for the project
VALID_CATEGORIES = [
    "GenAI", "Hardware", "Finance", "Coding", 
    "Security", "Cloud", "Other"
]

def categorize_article(content: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Use LLM to extract metadata from article content.
    
    Args:
        content: The markdown content of the article.
        model: OpenAI model to use (default: gpt-4o-mini).
        
    Returns:
        Dict with keys: title, category, summary.
        
    Raises:
        Exception: If LLM processing fails.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
        
    client = OpenAI(api_key=api_key)
    
    # Truncate content specifically for the prompt context window if needed, 
    # though 4o-mini has a large context. 
    # Sending first 15k chars is usually enough for categorization/summary.
    truncated_content = content[:15000]
    
    prompt = f"""
Analyze the following article content and provide:
1. A concise, filesystem-safe title (max 60 characters, alphanumeric and hyphens only).
2. A category strictly chosen from this list: {', '.join(VALID_CATEGORIES)}.
3. A one-sentence summary (max 150 characters).

Respond ONLY with a valid JSON object in this format:
{{
  "title": "Compact-Title-Here",
  "category": "GenAI",
  "summary": "This article discusses..."
}}

Article Content:
{truncated_content}
"""

    logger.info("Sending content to LLM for categorization...")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes technical articles."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("Empty response from LLM")
            
        data = json.loads(result_text)
        
        # Validate category
        if data.get("category") not in VALID_CATEGORIES:
            logger.warning(f"LLM returned invalid category '{data.get('category')}'. Defaulting to 'Other'.")
            data["category"] = "Other"
            
        return data
        
    except Exception as e:
        logger.error(f"LLM processing failed: {e}")
        raise
