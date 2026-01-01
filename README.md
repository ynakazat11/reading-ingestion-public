# Content Airlock

A system to aggregate technical articles from ad-hoc browsing and RSS feeds, process them with LLM categorization, and bundle them into digest files for NotebookLM upload.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Ingest a single article
python -m src.ingest "https://example.com/article"

# Poll RSS feeds for new content
python -m src.poll_rss

# Create weekly digest bundle
python -m src.bundle --days 7
```

## Project Structure

```
reading-ingestion/
├── data/           # Ingested articles organized by category
├── Digests/        # Bundled digest files for NotebookLM
├── src/
│   ├── ingest.py   # Core ingestion script
│   ├── poll_rss.py # RSS polling script
│   ├── bundle.py   # Digest bundler
│   └── utils/      # Jina and LLM client utilities
├── sources.json    # RSS feed configuration
└── requirements.txt
```

## Scripts

### `ingest.py`
Fetches a URL via Jina Reader, categorizes with LLM, and saves as Markdown.

```bash
python -m src.ingest "https://www.anthropic.com/news/claude-3-5-sonnet"
```

### `poll_rss.py`
Checks RSS feeds for new posts and ingests them automatically.

```bash
python -m src.poll_rss --hours 24
```

### `bundle.py`
Creates category-based digest files from recent articles.

```bash
python -m src.bundle --days 7 --category GenAI
```

## Categories

Default categories: `GenAI`, `Hardware`, `Finance`, `Coding`, `Security`, `Cloud`, `Other`

## Automation

GitHub Actions workflow runs:
- **Daily 8 AM UTC**: RSS polling
- **Friday 8 PM UTC**: Weekly bundle creation

## License

MIT
