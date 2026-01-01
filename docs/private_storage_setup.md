# Private Data Storage Setup

If you want to keep your **code public** (to share with others) but your **ingested articles private** (for security), you can configure Content Airlock to store data in a separate private repository.

## Overview

1.  **Public Repo**: Contains the scripts and workflows (where you are now).
2.  **Private Repo**: An empty repository that will store your `data/` and `Digests/`.
3.  **GitHub Action**: Connects the two.

## Step-by-Step Configuration

### 1. Create the Private Storage Repo
1.  Go to GitHub and create a new **Private** repository (e.g., `my-airlock-data`).
2.  Initialize it with a `README.md` so it's not empty.

### 2. Generate a Personal Access Token (PAT)
Since the Public Repo needs to write to the Private Repo, the default `GITHUB_TOKEN` is not enough.

1.  Go to [Settings > Developer settings > Tokens (classic)](https://github.com/settings/tokens).
2.  Generate a new token with the `repo` scope (Full control of private repositories).
3.  Copy the token.

### 3. Add Secrets to Public Repo
Go to your **Public Repo** > Settings > Secrets and variables > Actions.

Add the following secrets:
*   `STORAGE_REPO`: The name of your private repo (e.g., `username/my-airlock-data`).
*   `PAT_TOKEN`: The Personal Access Token you just copied.

### 4. (Optional) Update Local Setup
If you run scripts locally, you should also clone your private repo effectively:

```bash
# In your main project folder
git clone https://github.com/username/my-airlock-data storage
```

Then run commands pointing to it:
```bash
python -m src.ingest "https://..." --data-dir ./storage/data
```

## How it Works
The GitHub Workflows are configured to check:
- *If* `STORAGE_REPO` secret exists -> Checkout that private repo, save data there, and push to it.
- *If* `STORAGE_REPO` does not exist -> Save data to the current repo.
