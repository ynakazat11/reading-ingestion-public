# 📱 Save Articles from Your iPhone

This guide shows you how to save any article to your Content Airlock with **just 2 taps** from your iPhone!

---

## 🎯 What You'll Be Able to Do

When you're done, you can:
1. Find an interesting article in Safari
2. Tap the **Share** button  
3. Tap **"Save to Airlock"**  
4. ✨ Done! The article is saved automatically!

---

## 📋 Before You Start (One-Time Setup)

You'll need two things from GitHub:

### 1. Your GitHub Username
This is the name you use to log into GitHub.  
Example: If your profile is `github.com/coolperson123`, your username is **coolperson123**

### 2. A Special Password (called a "Token")

Think of this as a **special password** just for this app. Here's how to get one:

1. **Open this link on your phone:** [Create a GitHub Token](https://github.com/settings/tokens/new?scopes=repo&description=iOS%20Shortcut%20for%20Airlock)

2. **Log in** to GitHub if asked

3. You'll see a page with some boxes already checked. Just scroll down and tap **"Generate token"** (the green button)

4. **IMPORTANT:** You'll see a code that starts with `ghp_` — this is your special password!  
   📋 **Tap to copy it** and paste it somewhere safe (like Notes app) — you can only see it once!

---

## 🛠️ Create the Shortcut (5 minutes)

### Step 1: Open the Shortcuts App

Find and open the **Shortcuts** app on your iPhone (it comes pre-installed).

![Shortcuts app icon - blue square with overlapping colored squares](https://example.com/shortcuts-icon.png)

---

### Step 2: Create a New Shortcut

1. Tap the **+** button in the top right corner
2. Tap the name at the top and rename it to: **Save to Airlock**

---

### Step 3: Turn On Share Sheet

This lets the shortcut appear when you tap "Share" in Safari:

1. Tap the **ⓘ** button (bottom of screen)
2. Turn ON **"Show in Share Sheet"**
3. Tap **"Receives"** → uncheck everything EXCEPT:
   - ✅ URLs
   - ✅ Safari web pages
4. Tap **Done**

---

### Step 4: Add the Actions

Now we'll add 3 "blocks" that tell the shortcut what to do:

#### Block 1: Build the Message

1. Tap **"Add Action"**
2. Search for **"Text"** and tap it
3. In the text box, paste this **exactly**:

```
{"ref":"main","inputs":{"url":"URL_GOES_HERE"}}
```

4. Now we need to swap out `URL_GOES_HERE` with the actual article link:
   - Tap on the words `URL_GOES_HERE` in your text
   - Delete it
   - Tap **"Shortcut Input"** from the variables (or tap ✨ magic wand and find it)

Your text should now look like:
```
{"ref":"main","inputs":{"url":"[Shortcut Input]"}}
```

---

#### Block 2: Send to GitHub

1. Tap **"+"** to add another action
2. Search for **"Get Contents of URL"** and tap it
3. Tap the **URL** field and paste this (but change YOUR_USERNAME to your GitHub username):

```
https://api.github.com/repos/YOUR_USERNAME/reading-ingestion/actions/workflows/ingest_url.yml/dispatches
```

> **Example:** If your username is `coolperson123`, it would be:  
> `https://api.github.com/repos/coolperson123/reading-ingestion/actions/workflows/ingest_url.yml/dispatches`

4. Tap **"Show More"** to reveal extra options

5. Change **Method** to: **POST**

6. Tap **"Add new header"** and add these 3 headers:

   | Header Name | Value |
   |-------------|-------|
   | Accept | `application/vnd.github.v3+json` |
   | Authorization | `token YOUR_TOKEN_HERE` (replace with your ghp_xxx token!) |
   | User-Agent | `iOS Shortcut` |

7. Change **Request Body** to: **File**

8. Tap **File** and select the **Text** from Block 1

---

#### Block 3: Show a Confirmation (Optional but Nice!)

1. Tap **"+"** to add another action
2. Search for **"Show Notification"**
3. Set Title to: `✅ Saved!`
4. Set Body to: `Article sent to your Airlock`

---

### Step 5: Test It!

1. Open Safari and go to any article
2. Tap the **Share** button (the square with arrow)
3. Scroll down and tap **"Save to Airlock"**
4. You should see your notification! 🎉

---

## ✅ Checklist

Before testing, make sure:
- [ ] You changed `YOUR_USERNAME` to your actual GitHub username
- [ ] You pasted your token (the `ghp_xxx` code) in the Authorization header
- [ ] The token includes the word `token ` before it (with a space!)
- [ ] You selected "Shortcut Input" (not typed it as text)

---

## 🆘 Troubleshooting

### "Nothing happens when I tap Save to Airlock"
- Make sure your iPhone has internet
- Double-check your username is spelled correctly

### "I get an error"
- Make sure your token starts with `ghp_`
- Make sure you typed `token ` (with a space) before your token in Authorization
- Make sure you haven't expired your token on GitHub

### "I can't find the shortcut in Share menu"
- Go back to Step 3 and make sure "Show in Share Sheet" is ON
- Try closing Safari and opening it again

---

## 🎉 You Did It!

Your articles will now automatically:
1. Get fetched and cleaned up
2. Be categorized by topic  
3. Appear in your GitHub repo ready for NotebookLM!

> **Note:** It takes about 30-60 seconds for articles to appear in your repo after saving.

---

## 📝 Alternate Method: Email-Based (Even Easier!)

*Coming soon: We're working on an even simpler method where you can just email links to yourself!*
