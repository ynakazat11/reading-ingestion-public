# GitHub Automation Guide

Content Airlock uses GitHub Actions to automate the ingestion and bundling process. This means you don't need a server running 24/7.

## Workflows

### 1. Daily Pipeline (`daily_workflow.yml`)
This is the workhorse of the system.

**Triggers:**
*   **Schedule**: 
    *   RSS polling runs daily at **8:00 AM UTC**.
    *   Bundling runs every Friday at **8:00 PM UTC**.
*   **Manual**: You can manually trigger this from the "Actions" tab on GitHub.

**Jobs:**
*   `poll-rss`: Checks configured RSS feeds for new content in the last 24 hours.
*   `bundle-weekly`: Scans the `data/` folder for the last 7 days of articles and creates a digest in `Digests/`.

### 2. Ingest URL Only (`ingest_url.yml`)
This workflow allows you to "push" a single URL into the system on demand.

**Triggers:**
*   **Workflow Dispatch**: Requires a `url` input.
*   **API Trigger**: Used by the iOS Shortcut.

**Jobs:**
*   `ingest-ad-hoc`: Runs `ingest.py` for the provided URL and commits the result.

## Configuration

To modify the schedule or behavior, edit the YAML files in `.github/workflows/`.

### Changing the Schedule
Open `daily_workflow.yml` and find the cron expressions:

```yaml
on:
  schedule:
    - cron: '0 8 * * *'  # Change this for polling time
```
Use [crontab.guru](https://crontab.guru/) to generate new expressions.

### Secrets
The workflows require secrets to function. Go to **Settings > Secrets and variables > Actions** in your repo.

*   `OPENAI_API_KEY`: **Required**. Used for categorization and summarization.
*   `JINA_API_KEY`: **Optional**. Add this if you hit rate limits with Jina Reader.
