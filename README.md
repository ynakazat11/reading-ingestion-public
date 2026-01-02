# Content Airlock

> [!CAUTION]
> **DO NOT USE THIS REPOSITORY DIRECTLY FOR YOUR PERSONAL CONTENT**
> 
> This is a **public template** for the Content Airlock system. If you want to use this for yourself:
> 1. **Fork this repository** to your own GitHub account
> 2. **Make your fork PRIVATE** (Settings → General → Danger Zone → Change visibility)
> 3. Follow the setup instructions in your private fork
>
> 🔒 **Why Private?** This system processes personal emails and browsing history. GitHub Actions workflows are configured to **only run on private repositories** for your safety.

A system to aggregate technical articles from ad-hoc browsing and RSS feeds, process them with LLM categorization, and bundle them into digest files for NotebookLM upload.

## 🚀 For Your Own Use

Want to set up your own instance? See **[GETTING_STARTED.md](GETTING_STARTED.md)** for step-by-step instructions on forking and configuring your private copy.

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

## Categories

Articles are automatically categorized into these textbook-style categories:

| Category | Description |
|----------|-------------|
| `ML-Fundamentals` | Core ML theory, math, algorithms |
| `LLM-Architecture` | Transformers, attention, model design |
| `LLM-Training` | Pre-training, fine-tuning, RLHF |
| `LLM-Inference` | Serving, optimization, quantization |
| `Prompt-Engineering` | Prompting techniques, chain-of-thought |
| `AI-Agents` | Agentic systems, tool use, planning |
| `ML-Applications` | Computer vision, NLP, recommenders |
| `ML-Ops` | Training infra, deployment, monitoring |
| `Systems` | Distributed systems, databases |
| `Security` | Cybersecurity, privacy, AI safety |
| `Software-Engineering` | Architecture, testing, best practices |
| `Hardware` | GPUs, chips, edge devices |
| `Product-Management` | Strategy, metrics, roadmaps |
| `Other` | Anything else |

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

## ⚠️ Privacy & Disclaimer

**IMPORTANT PRIVACY NOTICE**

This software processes sensitive personal information including:
- Email communications sent to your specified inbox
- URLs from your browsing history
- Content from articles you read

> [!WARNING]
> **YOU ARE SOLELY RESPONSIBLE FOR PROTECTING YOUR DATA**
> 
> - **NEVER run this software in a public repository** with your personal data
> - The built-in workflow safety checks are designed to prevent accidental exposure, but **you remain solely responsible** for ensuring your repository visibility settings are correct
> - The authors and contributors of this software **assume NO liability** for any data exposure, privacy breaches, or damages resulting from misconfiguration or misuse
> - This software is provided "AS IS" without warranty of any kind (see LICENSE)

**BY USING THIS SOFTWARE, YOU ACKNOWLEDGE THAT:**
1. You understand the privacy risks associated with processing personal data
2. You will only use this software in a properly secured, **private repository**
3. You accept **full responsibility** for any privacy breaches or data exposure
4. The authors and contributors are **NOT liable** for any direct, indirect, incidental, special, exemplary, or consequential damages arising from your use or misuse of this software

For complete legal terms, see the [MIT License](LICENSE) included with this software.


## License

MIT
