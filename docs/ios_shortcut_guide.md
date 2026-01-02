# 📱 Save Articles from Your iPhone

Send any article to your Content Airlock by **sharing it to email**. No tokens, no complicated setup — just share!

---

## 🎯 How It Works

1. Find an interesting article
2. Tap **Share** → **Mail**
3. Send it to your special Airlock email address
4. ✨ Done! The article appears in your GitHub repo the next day!

That's it. No apps to install, no passwords stored on your phone.

---

## � Pro Strategy for Alias Users (Highly Recommended)

If you use a Gmail alias (like `you+airlock@gmail.com`), the emails show up in your main inbox. If you accidentally click them, the system might skip them because they aren't "unread" anymore.

**Here is the perfect fix (5 minutes):**

### 1. Create an "Airlock" Label in Gmail
- Open Gmail on your computer.
- On the left, scroll down and click **"Create new label"**.
- Name it: `Airlock`

### 2. Set Up a Filter
- Click the **Search options** icon (the sliders) in the Gmail search bar.
- In the **"To"** field, type your alias: `you+airlock@gmail.com`
- Click **"Create filter"**.
- Check these boxes:
  - [x] **Skip the Inbox (Archive it)**
  - [x] **Apply the label:** Choose `Airlock`
- Click **"Create filter"**.

### 3. Update Your GitHub Secrets
Add these new secrets so the system knows to look in your special folder and empty it when done:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AIRLOCK_EMAIL_FOLDER` | `Airlock` | Tells the system to check your new folder |
| `AIRLOCK_EMAIL_ACTION` | `delete` | Tells the system to "cleanup" (Trash) after ingestion |
| `AIRLOCK_EMAIL_UNREAD_ONLY` | `False` | Processes everything in the folder, even if you read it |

---

## �📋 One-Time Setup (10 minutes)

### Step 1: Create a Dedicated Email Address

You have two options:

**Option A: Use an alias of your existing Gmail (Recommended)**
- Your existing Gmail already supports aliases!
- If your email is `yourname@gmail.com`, you can use `yourname+airlock@gmail.com`
- All emails to that address go to your regular inbox
- No new account needed!

**Option B: Create a new Gmail account**
- Go to [Gmail](https://mail.google.com) and create a new account
- Example: `yourname.airlock@gmail.com`
- This keeps Airlock emails separate from personal mail

---

### Step 2: Create an App Password

Gmail requires a special "App Password" for the ingestion system to read your emails. This is NOT your regular Gmail password.

1. **Go to:** [Google App Passwords](https://myaccount.google.com/apppasswords)

2. **Sign in** to the Gmail account you'll use for Airlock

3. **Create an app password:**
   - App name: `Content Airlock`
   - Click **Create**

4. **Copy the 16-character password** that appears (like `xxxx xxxx xxxx xxxx`)
   - ⚠️ Save this somewhere safe — you won't see it again!

> **Note:** If you don't see the App Passwords option, you need to [enable 2-Step Verification](https://myaccount.google.com/signinoptions/two-step-verification) first.

---

### Step 3: Add Secrets to GitHub

Go to your repository's secrets page:  
`Settings > Secrets and variables > Actions`

Add these secrets so the automation can run:

| Secret Name | Value | Required? |
|-------------|-------|-----------|
| `OPENAI_API_KEY` | Your OpenAI API key (`sk-...`) | ✅ **CRITICAL** |
| `AIRLOCK_EMAIL` | Your Airlock email (e.g., `yourname+airlock@gmail.com`) | ✅ Yes |
| `AIRLOCK_EMAIL_PASSWORD` | The 16-character App Password from Step 2 | ✅ Yes |
| `AIRLOCK_ALLOWED_SENDERS` | Your personal email address(es) | 🔒 Recommended |

> [!IMPORTANT]
> **Don't forget the `OPENAI_API_KEY`!** Even if you set up the email correctly, the system needs the AI key to "read" and categorize your articles.

#### 🔒 About Sender Allowlist

**`AIRLOCK_ALLOWED_SENDERS`** is a security feature that ensures only emails from **your** email addresses are processed. This prevents someone from spamming your Airlock inbox with malicious URLs.

**Examples:**
- Single sender: `yourname@gmail.com`
- Multiple senders: `yourname@gmail.com,yourname@icloud.com`

If you don't set this, all emails to your Airlock address will be processed — which is fine if you keep the email address private, but the allowlist adds an extra layer of protection.

That's it! The system is now configured.

---

## 📱 Using It from Your iPhone

### Saving an Article

1. **Open any article** in Safari, Chrome, or any app
2. **Tap the Share button** (square with arrow pointing up)
3. **Tap Mail**
4. **In the "To:" field**, type your Airlock email address
5. **Tap Send** (you don't need to add a subject or body!)

The article URL will be automatically extracted from the email and ingested!

### Pro Tip: Add to Contacts

Add your Airlock email as a contact named "📚 Airlock" so it appears at the top of your contacts when sharing.

1. Open the **Contacts** app
2. Tap **+** to add a new contact
3. Name: `📚 Airlock`
4. Email: `yourname+airlock@gmail.com`
5. Save!

Now when you share via Mail, just type "Airlock" and it autocompletes!

---

## 📦 Batching Multiple Articles

The Airlock is smart! You can send multiple links in a single email, and it will process all of them as separate articles.

### How to do it:
1. **Copy** several links throughout the day (into your Notes app or a Draft email).
2. **Send one email** containing all the links to your Airlock address.
3. Every link found in the email will be extracted and saved individually.

This is a great way to "clear out" your open Safari tabs at the end of the day!

---

## ⏱️ What Happens Next

1. **Once daily at 8 AM UTC**, GitHub checks your Airlock inbox
2. It finds new emails and extracts any URLs
3. Each article is fetched, cleaned, and categorized
4. The article appears in your `data/` folder (or private storage repo)
5. The email is marked as read

---

## 🎨 Bonus: Create a Shortcut for Even Faster Sharing

If you want to skip the Mail app entirely, you can create a simple shortcut that pre-fills the email:

1. Open the **Shortcuts** app
2. Tap **+** to create a new shortcut
3. Name it: **Send to Airlock**
4. Add these actions:
   - **Get URLs from Input** (receives from Share Sheet)
   - **Send Email**:
     - To: `yourname+airlock@gmail.com`
     - Subject: (leave empty)
     - Body: Select the **URLs** variable
     - **Turn ON "Show Compose Sheet"** (so you can review before sending)
5. Tap the **(i)** button and enable **Show in Share Sheet**

Now you can share directly to your Airlock shortcut!

---

## 🔧 Troubleshooting

### Articles aren't appearing
- Check your GitHub Actions: `https://github.com/YOUR_USERNAME/reading-ingestion/actions`
- Make sure the `AIRLOCK_EMAIL` and `AIRLOCK_EMAIL_PASSWORD` secrets are set
- Verify the App Password is correct (no spaces)

### "Authentication failed" error in Actions
- Your App Password may have expired or been revoked
- Create a new App Password and update the GitHub secret

### Emails still showing as unread
- The system marks emails as read after processing
- If there's an error during processing, the email stays unread for retry

---

## 🔒 Security Notes

- **No tokens on your phone**: Your GitHub credentials stay in GitHub
- **App Password is limited**: It can only read email, not change your password
- **Private by default**: If you've configured private storage, articles go there

---

## 📱 Using Other Email Apps

This works with ANY app that can share via email:

- **Safari**: Share → Mail
- **Chrome**: Share → Mail  
- **Twitter/X**: Share → Mail
- **Pocket**: Share → Mail
- **Any app with a Share button!**
