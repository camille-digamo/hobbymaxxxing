# Google Sheets API Setup Guide

## Step 1: Use the Same Google Cloud Project

1. **Return to Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Select your project**: Choose the `hobby-maxxxer-bot` project you created for YouTube API

## Step 2: Enable Google Sheets API

1. **Navigate to APIs & Services → Library**
2. **Search for "Google Sheets"**:
   - Type "Google Sheets API" in the search box
   - Click on "Google Sheets API"
3. **Enable the API**: Click "Enable"

## Step 3: Create a Service Account

1. **Go to IAM & Admin → Service Accounts**:
   - In the left sidebar, click "IAM & Admin" → "Service Accounts"
2. **Create Service Account**:
   - Click "+ CREATE SERVICE ACCOUNT"
   - Service account name: `hobbymaxxxing-sheets`
   - Service account ID: (auto-generated, like `hobbymaxxxing-sheets@hobby-maxxxer-bot.iam.gserviceaccount.com`)
   - Click "CREATE AND CONTINUE"
3. **Skip role assignment**: Click "CONTINUE" (we don't need special roles)
4. **Skip user access**: Click "DONE"

## Step 4: Create Service Account Key

1. **Click on your new service account** in the list
2. **Go to the "Keys" tab**
3. **Add a key**:
   - Click "ADD KEY" → "Create new key"
   - Choose "JSON" format
   - Click "CREATE"
4. **Download the JSON file**:
   - Your browser will download a file like `hobby-maxxxer-bot-1a2b3c4d5e6f.json`
   - **IMPORTANT**: Move this file to your project's `auth/` folder
   - Rename it to `hobbymaxxxing-service-account.json` for consistency

## Step 5: Create Your Google Sheet

1. **Create a new Google Sheet**: Go to [sheets.google.com](https://sheets.google.com)
2. **Create blank spreadsheet**
3. **Set up the sheet structure**:

### Topics Sheet:
Create a sheet named "topics" with these columns:
```
A1: topic
B1: parent_topic  
C1: last_watched
D1: videos_watched
E1: interest_score
```

### Videos Sheet:
Create a sheet named "videos" with these columns:
```
A1: video_title
B1: channel
C1: video_url
D1: topic
E1: parent_topic
F1: date_recommended
G1: date_watched
H1: rating
I1: notes
```

## Step 6: Share Sheet with Service Account

1. **Copy the service account email**:
   - From your JSON file, find the `"client_email"` field
   - It looks like: `hobbymaxxxing-sheets@hobby-maxxxer-bot.iam.gserviceaccount.com`
2. **Share the sheet**:
   - In your Google Sheet, click "Share" (top right)
   - Paste the service account email
   - Set permission to "Editor"
   - **Uncheck** "Notify people" (it's a bot, not a person)
   - Click "Share"

## Step 7: Get Your Sheet ID

1. **Copy the Sheet ID** from your URL:
   - Your sheet URL looks like: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`
   - The Sheet ID is the long string between `/d/` and `/edit`
   - Example: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

## Step 8: Add to Your Environment

Add to your `.env` file:
```env
GOOGLE_SHEETS_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_SERVICE_ACCOUNT_FILE=auth/hobbymaxxxing-service-account.json
```

## Troubleshooting

**❌ "Service account not found" error**:
- Make sure you shared the sheet with the service account email
- Check the email exactly matches what's in your JSON file

**❌ "Permission denied" error**:
- Ensure the service account has "Editor" access to your sheet
- Try creating a fresh service account and JSON key

**❌ "File not found" error**:
- Verify the JSON file is in the `auth/` folder
- Check the filename matches what's in your `.env` file

**Need help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) for more solutions.