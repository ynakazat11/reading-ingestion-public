# Getting Started with Content Airlock

This repository is a **template** for building your own personal content aggregation system. Follow these steps to set up your own private instance.

## Step 1: Fork This Repository

1. Click the **Fork** button at the top of this page
2. Choose your GitHub account as the destination

## Step 2: Make Your Fork Private

🔒 **CRITICAL**: You must make your fork private before setting up automation.

1. Go to your fork's **Settings** tab
2. Scroll to **General** → **Danger Zone**
3. Click **Change visibility** → **Make private**
4. Confirm by typing the repository name

> [!WARNING]
> **GitHub Actions workflows will refuse to run on public repositories** as a safety measure. They will fail with a clear error message if your repository is not private.

> [!CAUTION]
> **Privacy Disclaimer**: You are solely responsible for protecting your personal data. The authors of this software assume no liability for any privacy breaches or data exposure. See [Privacy & Disclaimer](README.md#️-privacy--disclaimer) for full details.


## Step 3: Follow Setup Instructions

Now that you have a private fork, follow the setup in [README.md](README.md):

1. Install dependencies: `pip install -r requirements.txt`
2. Configure your API keys (see README for details)
3. Set up GitHub secrets for automation
4. Optionally configure email ingestion or private storage

## Why Private?

Content Airlock processes:
- Personal emails sent to your inbox
- URLs from your browsing history  
- Articles you're reading

Making your repository private ensures this personal data stays secure and is not exposed publicly.

## What Happens if I Keep it Public?

The workflows are designed with safety in mind:
- They will **immediately fail** with a privacy warning
- No data will be processed
- No emails will be read
- You'll see a clear error message explaining the issue

This is intentional—it prevents accidental data exposure.

## Next Steps

Once your repository is private, check out:
- **[📱 iOS/Mobile Setup](docs/ios_shortcut_guide.md)**: Save articles from your phone
- **[🔐 Private Storage Setup](docs/private_storage_setup.md)**: Keep articles in a separate private repo
- **[⚙️ GitHub Automation](docs/github_automation.md)**: Understand the automated workflows
