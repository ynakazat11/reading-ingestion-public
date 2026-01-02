import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

# Valid categories for the project - organized like textbook sections
VALID_CATEGORIES = [
    "ML-Fundamentals",       # Core ML theory, math, algorithms, statistics
    "LLM-Architecture",      # Transformers, attention mechanisms, model design
    "LLM-Training",          # Pre-training, fine-tuning, RLHF, datasets
    "LLM-Inference",         # Serving, optimization, quantization, latency
    "Prompt-Engineering",    # Prompting techniques, chain-of-thought, few-shot
    "AI-Agents",             # Agentic systems, tool use, planning, reasoning
    "ML-Applications",       # Computer vision, NLP apps, recommenders, speech
    "ML-Ops",                # Training infra, deployment, monitoring, MLOps
    "Systems",               # Distributed systems, databases, networking
    "Security",              # Cybersecurity, cryptography, privacy, AI safety
    "Software-Engineering",  # Architecture, testing, best practices, design
    "Hardware",              # GPUs, chips, edge devices, custom silicon
    "Product-Management",    # Strategy, metrics, roadmaps, team management
    "Other",                 # Anything that doesn't fit above
]

# Category descriptions for LLM guidance
CATEGORY_DESCRIPTIONS = """
- ML-Fundamentals: Core ML theory, math foundations, classical algorithms, statistics
- LLM-Architecture: Transformer design, attention mechanisms, model architecture papers
- LLM-Training: Pre-training methods, fine-tuning, RLHF, dataset curation
- LLM-Inference: Model serving, latency optimization, quantization, deployment
- Prompt-Engineering: Prompting techniques, chain-of-thought, few-shot learning
- AI-Agents: Autonomous agents, tool use, planning, multi-step reasoning
- ML-Applications: Vision, NLP tasks, recommendation systems, speech, specific use cases
- ML-Ops: Training infrastructure, model deployment, monitoring, pipelines
- Systems: Distributed computing, databases, networking, infrastructure
- Security: Cybersecurity, AI safety, privacy, cryptography, adversarial attacks
- Software-Engineering: Code design, testing, best practices, architecture patterns
- Hardware: GPUs, TPUs, custom chips, edge devices, accelerators
- Product-Management: Strategy, metrics, roadmaps, team leadership
- Other: Content that doesn't fit the above categories
"""

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
You are categorizing technical articles for a knowledge base, similar to organizing chapters in a CS/AI textbook.

Analyze the article and provide:
1. A concise, filesystem-safe title (max 60 chars, alphanumeric and hyphens only).
2. A category from the list below. Choose the MOST SPECIFIC category that fits.
3. A one-sentence summary (max 150 chars).

CATEGORIES:
{CATEGORY_DESCRIPTIONS}

RULES:
- Pick the most specific category. E.g., an article about RLHF → "LLM-Training", not "ML-Fundamentals".
- Agent-related content (tool use, planning, autonomous systems) → "AI-Agents".
- Architecture papers (new model designs, attention variants) → "LLM-Architecture".
- Prompting tips/techniques → "Prompt-Engineering".
- Only use "Other" if nothing else fits.

Respond ONLY with valid JSON:
{{
  "title": "Compact-Title-Here",
  "category": "LLM-Training",
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
