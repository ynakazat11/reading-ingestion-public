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

# Poll email inbox for shared URLs
python -m src.email_ingestion

# Create weekly digest bundle
python -m src.bundle --days 7
```

## 📱 Mobile Ingestion

**Save articles from your iPhone in 2 taps!** Just share any article to email.

See the [iOS Setup Guide](docs/ios_shortcut_guide.md) for easy setup instructions.

## Project Structure

```
reading-ingestion/
├── data/                # Ingested articles organized by category
├── Digests/             # Bundled digest files for NotebookLM
├── src/
│   ├── ingest.py        # Core ingestion script
│   ├── poll_rss.py      # RSS polling script
│   ├── email_ingestion.py # Email inbox polling
│   ├── bundle.py        # Digest bundler
│   └── utils/           # Jina and LLM client utilities
├── sources.json         # RSS feed configuration
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

### `email_ingestion.py`
Polls an email inbox for URLs shared from mobile devices.

```bash
python -m src.email_ingestion --dry-run  # Preview without processing
```

### `bundle.py`
Creates category-based digest files from recent articles.

```bash
python -m src.bundle --days 7 --category GenAI
```

Default categories: `GenAI`, `Hardware`, `Finance`, `Coding`, `Security`, `Cloud`, `Other`

## ⚙️ GitHub Setup (Required for Automation)

To make the daily automation work, you must add your API keys to your GitHub repository secrets:

1.  Go to your repo on GitHub: **Settings > Secrets and variables > Actions**
2.  Click **New repository secret** for each of these:

| Secret Name | Description | Required? |
|-------------|-------------|-----------|
| `OPENAI_API_KEY` | Your OpenAI API key (`sk-...`) | ✅ Yes |
| `AIRLOCK_EMAIL` | Your Airlock email (e.g., `you+airlock@gmail.com`) | 📱 For Mobile |
| `AIRLOCK_EMAIL_PASSWORD` | Your Email App Password (16 chars) | 📱 For Mobile |
| `PAT_TOKEN` | A GitHub Classic Token (for private storage) | 🔐 For Private Repo |
| `STORAGE_REPO` | `username/repo-name` for private storage | 🔐 For Private Repo |

*Optional: Set `LLM_PROVIDER=gemini` and `GOOGLE_API_KEY` if you prefer Google's models.*

## Automation

GitHub Actions workflow runs:
- **Daily 8 AM UTC**: Email inbox + RSS feed polling
- **Friday 8 PM UTC**: Weekly bundle creation

## User Guides 📚

*   **[📱 iOS/Mobile Setup](docs/ios_shortcut_guide.md)**: Save articles from your phone via email — no tokens needed!
*   **[🔐 Private Storage Setup](docs/private_storage_setup.md)**: Keep your articles in a private repo.

## License

MIT
