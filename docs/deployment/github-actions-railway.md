# GitHub Actions + Railway Hybrid Setup

## Overview

This setup combines the best of both worlds:
- **GitHub Actions** (FREE): Sends daily video recommendations
- **Railway** ($0-3/month): Persistent bot for reactions and topic exploration

**Perfect for**: Non-technical friends who want cloud reliability without high costs.

**Total Cost**: $0-3/month (Railway free tier covers most usage)

## Part 1: GitHub Actions Setup (Daily Videos)

### Step 1: Fork the Repository

1. **Go to the project's GitHub page**
2. **Click "Fork"** (top right)
3. **Create fork** in your GitHub account

### Step 2: Add Your API Keys as Secrets

1. **Go to your forked repository**
2. **Click "Settings" tab** (top of repo)
3. **Go to "Secrets and variables" → "Actions"**
4. **Add each secret** by clicking "New repository secret":

**Required Secrets**:
- `YOUTUBE_API_KEY`: Your YouTube API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key  
- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `DISCORD_CHANNEL_ID`: Your Discord channel ID (numbers only)
- `DISCORD_USER_ID`: Your Discord user ID (numbers only)
- `GOOGLE_SHEETS_ID`: Your Google Sheets document ID
- `GOOGLE_SERVICE_ACCOUNT_JSON`: **Entire contents** of your service account JSON file

**For the JSON secret**:
1. Open your service account JSON file in a text editor
2. Copy **everything** (including the curly braces)
3. Paste it as the value for `GOOGLE_SERVICE_ACCOUNT_JSON`

### Step 3: Enable GitHub Actions

1. **Go to "Actions" tab** in your repository
2. **Enable workflows** (if prompted)
3. **Find "Daily Hobby Video Recommendation"** workflow
4. **Click "Enable workflow"**

### Step 4: Test the Daily Job

1. **Go to "Actions" tab**
2. **Click on "Daily Hobby Video Recommendation"**
3. **Click "Run workflow"** (to test immediately)
4. **Watch the workflow run** - should complete in ~2 minutes
5. **Check Discord** - you should see a video recommendation!

## Part 2: Railway Setup (Persistent Listener)

### Step 5: Create Railway Account

1. **Visit [railway.app](https://railway.app)**
2. **Sign up** with GitHub account (easiest)
3. **Verify your email**

### Step 6: Deploy the Listener Service

1. **Click "New Project"** in Railway
2. **Select "Deploy from GitHub repo"**
3. **Choose your forked repository**
4. **Railway will automatically**:
   - Detect Python project
   - Install dependencies
   - Use the `config/railway.json` configuration

### Step 7: Add Environment Variables

1. **Go to your Railway project dashboard**
2. **Click on your service**
3. **Go to "Variables" tab**
4. **Add each variable**:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=123456789012345678
DISCORD_USER_ID=987654321098765432
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_SERVICE_ACCOUNT_FILE=/tmp/service-account.json
```

5. **Add the JSON content**:
   - Variable name: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Value: Paste your entire service account JSON content

### Step 8: Deploy and Monitor

1. **Railway will auto-deploy** after adding variables
2. **Check deployment logs**:
   - Go to "Deployments" tab
   - Click on latest deployment
   - View logs to ensure no errors
3. **Verify it's working**:
   - Bot should show as online in Discord
   - Try reacting to a video - should prompt for notes

## How It Works

### Daily Video Flow (GitHub Actions):
```
9:00 AM EST daily → GitHub Actions runs → 
Finds topic → Gets Claude recommendation → 
Posts to Discord with reactions → Exits
```

### Persistent Features (Railway):
```
24/7 listening → User reacts to video → 
Bot prompts for notes → Saves to Google Sheets →
Handles topic exploration anytime
```

## Customization

### Change Daily Time

Edit `.github/workflows/daily-hobby.yml` in your fork:
```yaml
schedule:
  # Change this cron expression
  # Format: minute hour * * *
  - cron: '0 14 * * *'  # 2 PM UTC = 9 AM EST
```

**Common times**:
- 8 AM EST: `0 13 * * *` 
- 9 AM EST: `0 14 * * *`
- 10 AM EST: `0 15 * * *`
- 6 PM EST: `0 23 * * *`

### Pause Daily Videos

**Temporarily**: 
1. Go to Actions tab → "Daily Hobby Video Recommendation"
2. Click "Disable workflow"

**Permanently**: Delete the `.github/workflows/daily-hobby.yml` file

## Cost Monitoring

### GitHub Actions:
- **Completely FREE** for public repositories
- **2,000 minutes/month FREE** for private repositories
- Each daily job uses ~2 minutes
- 30 days = 60 minutes used (well within free tier)

### Railway:
- **Free Tier**: $0/month (550 hours of usage)  
- **Paid Tier**: $5/month (unlimited)
- Listener service uses ~24 hours/day = 720 hours/month
- **Expected cost**: $0-3/month (Railway may offer free tier extensions)

## Troubleshooting

**❌ GitHub Actions failing**:
- Check "Actions" tab for error messages
- Verify all secrets are added correctly
- Ensure `GOOGLE_SERVICE_ACCOUNT_JSON` contains the full JSON

**❌ Railway deployment failing**:
- Check deployment logs for errors
- Verify environment variables are set
- Make sure Railway detected the Python project correctly

**❌ Bot not responding to reactions**:
- Check Railway service logs
- Verify the listener service is running (not crashed)
- Test that Discord bot has proper permissions

**❌ Daily videos not posting**:
- Check if GitHub Actions workflow is enabled
- Look at workflow run history in Actions tab
- Verify cron schedule is correct for your timezone

**Need help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) for more solutions.