# YouTube Data API Setup Guide

## Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**: Visit [console.cloud.google.com](https://console.cloud.google.com)
2. **Sign in** with your Google account
3. **Create a new project**:
   - Click "Select a project" dropdown at the top
   - Click "New Project"
   - Enter project name: `hobby-maxxxer-bot`
   - Click "Create"

## Step 2: Enable YouTube Data API

1. **Navigate to APIs & Services**:
   - In the left sidebar, click "APIs & Services" → "Library"
2. **Search for YouTube**:
   - Type "YouTube Data API v3" in the search box
   - Click on "YouTube Data API v3"
3. **Enable the API**:
   - Click the "Enable" button
   - Wait for it to activate (takes 30 seconds)

## Step 3: Create API Credentials

1. **Go to Credentials**:
   - In the left sidebar, click "APIs & Services" → "Credentials"
2. **Create API Key**:
   - Click "+ CREATE CREDENTIALS" at the top
   - Select "API key"
3. **Copy your API key**:
   - A popup will show your new API key
   - **IMPORTANT**: Copy this key immediately - you'll need it for your `.env` file
   - Example: `AIzaSyBvOiM2K8J3L4N5O6P7Q8R9S0T1U2V3W4X5Y6Z7`

## Step 4: Secure Your API Key (Recommended)

1. **Restrict the API key**:
   - Click "RESTRICT KEY" in the popup (or edit the key later)
   - Under "API restrictions", select "Restrict key"
   - Choose "YouTube Data API v3" from the dropdown
   - Click "Save"

## Step 5: Add to Your Environment

Add your YouTube API key to your `.env` file:
```env
YOUTUBE_API_KEY=AIzaSyBvOiM2K8J3L4N5O6P7Q8R9S0T1U2V3W4X5Y6Z7
```

## Troubleshooting

**❌ "API key not valid" error**:
- Make sure you copied the entire key (no extra spaces)
- Check that YouTube Data API v3 is enabled in your project
- Wait 5-10 minutes for the API to fully activate

**❌ "Quota exceeded" error**:
- YouTube API has daily limits (10,000 requests per day for free)
- The bot uses ~3-5 requests per video recommendation
- Upgrade to paid plan if needed (rare for personal use)

**Need help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) for more solutions.