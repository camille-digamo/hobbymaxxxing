# Discord Bot Setup Guide

## Step 1: Create a Discord Application

1. **Go to Discord Developer Portal**: [discord.com/developers/applications](https://discord.com/developers/applications)
2. **Sign in** with your Discord account
3. **Create New Application**:
   - Click "New Application" (top right)
   - Name: `Hobby Maxxxer Bot`
   - Accept Terms of Service
   - Click "Create"

## Step 2: Create the Bot

1. **Go to Bot Section**:
   - In the left sidebar, click "Bot"
2. **Create Bot**:
   - Click "Add Bot" (if not already created)
   - Confirm by clicking "Yes, do it!"

## Step 3: Configure Bot Settings

1. **Bot Permissions** (Important!):
   - **Privileged Gateway Intents**:
     - ✅ Enable "Message Content Intent" (required for reading messages)
     - ✅ Enable "Server Members Intent" (recommended)
   - **Public Bot**: 
     - ❌ Disable "Public Bot" (keep it private for security)

2. **Copy Bot Token**:
   - Under "Token" section, click "Copy"
   - **IMPORTANT**: Save this token immediately - you'll need it for your `.env` file

## Step 4: Set Bot Permissions

1. **Go to OAuth2 → URL Generator**:
   - In the left sidebar, click "OAuth2" → "URL Generator"
2. **Select Scopes**:
   - ✅ Check "bot"
3. **Select Bot Permissions**:
   - ✅ Send Messages
   - ✅ Send Messages in Threads  
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use Slash Commands (optional, for future features)

## Step 5: Invite Bot to Your Server

1. **Copy the Generated URL** from the bottom of the page
2. **Open the URL** in a new tab
3. **Select Your Server**:
   - Choose the Discord server where you want the bot
   - You must have "Manage Server" permissions
4. **Authorize the Bot**: Click "Authorize"

## Step 6: Set Up Your Discord Channel

1. **Create or Choose a Channel**:
   - Create a dedicated channel like `#hobby-videos` 
   - Or use an existing channel
2. **Get Channel ID**:
   - **Enable Developer Mode**: User Settings → Advanced → Developer Mode (ON)
   - **Right-click your channel** → "Copy Channel ID"
   - Example: `123456789012345678`
3. **Get Your User ID**:
   - **Right-click your profile** (anywhere in Discord) → "Copy User ID"
   - Example: `987654321098765432`

## Step 7: Test Bot Permissions

1. **Check Bot is Online**:
   - Your bot should appear in the member list (might be under "Offline" until you start it)
2. **Test Channel Access**:
   - Make sure the bot can see your chosen channel
   - If not, check channel permissions for the bot role

## Step 8: Add to Your Environment

Add to your `.env` file:
```env
DISCORD_BOT_TOKEN={token}
DISCORD_CHANNEL_ID={copy_channel_id_after_enabling_discord_dev_settings}
DISCORD_USER_ID={copy_user_id_after_enabling_discord_dev_settings}
```

## Troubleshooting

**❌ "Bot not responding" error**:
- Make sure "Message Content Intent" is enabled in Bot settings
- Check that the bot has "Send Messages" permission in your channel
- Verify the bot token is correct (no extra spaces)

**❌ "Missing Permissions" error**:
- Re-invite the bot with the correct permissions
- Check channel-specific permissions (right-click channel → Edit Channel → Permissions)

**❌ "Invalid User ID" error**:
- Make sure you copied YOUR user ID, not the bot's user ID
- Developer Mode must be enabled to see "Copy User ID" option

**❌ Bot appears offline**:
- This is normal until you start running the bot code
- The bot will show as online once you run `python main.py`

**Need help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) for more solutions.