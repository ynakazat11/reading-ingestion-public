# How to Create an iOS Shortcut for Content Airlock

This guide explains how to create an iOS Shortcut on your iPhone/iPad that sends any URL directly to your Content Airlock system for ingestion.

## Prerequisites

1.  **GitHub Account**
2.  **Personal Access Token (PAT)**:
    *   Go to [GitHub Settings > Developer parameters > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens).
    *   Generate new token (classic).
    *   Select scopes: `repo` (Full control of private repositories).
    *   **Copy the token immediately**. You won't see it again.

## Step-by-Step Shortcut Creation

1.  Open the **Shortcuts** app on your iPhone.
2.  Tap **+** to create a new shortcut.
3.  Name it **"Send to NotebookLM"** (or whatever you prefer).
4.  Enable it for the Share Sheet:
    *   Tap the **(i)** info icon at the bottom.
    *   Toggle **Show in Share Sheet**.
    *   At the top, it will say "Receive **Any** input from **Share Sheet**". Tap **Any** and uncheck everything except **URLs** and **Safari Web Pages**.

### The Logic Flow

Add the following actions in order:

**1. Dictionary** (Action: "Dictionary")
*   Add a new item:
    *   Key: `ref`
    *   Text: `main` (or your branch name)
*   Add a new item:
    *   Key: `inputs`
    *   Type: **Dictionary**
    *   Inside this nested dictionary, add:
        *   Key: `url`
        *   Value: Select variable **Shortcut Input**

**2. Get Contents of URL** (Action: "Get Contents of URL")
*   URL: `https://api.github.com/repos/YOUR_USERNAME/reading-ingestion/actions/workflows/ingest_url.yml/dispatches`
    *   *Replace `YOUR_USERNAME` with your GitHub username.*
*   Method: **POST**
*   **Headers**:
    *   `Accept`: `application/vnd.github.v3+json`
    *   `Authorization`: `token ghp_xxxxxxxxxxxx` (Paste your PAT here)
    *   `User-Agent`: `iOS Shortcut`
*   **Request Body**: **File**
*   **File**: Select the **Dictionary** variable from Step 1.

**3. Show Notification** (Optional)
*   Title: "Airlock Activated"
*   Body: "Sent to ingestion queue."

## How to Use

1.  Open an article in Safari or Chrome on iOS.
2.  Tap the **Share** button.
3.  Select **Send to Content Airlock**.
4.  The shortcut will trigger the GitHub Action `Ingest URL`.
5.  Wait ~30-60 seconds, and the new file will appear in your repo's `data/` folder!
