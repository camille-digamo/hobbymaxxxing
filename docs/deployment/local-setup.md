# Local Deployment Guide

## Overview

Local deployment runs the bot on your own computer or server. This is the **cheapest option** (completely free) and gives you full control, but requires keeping your computer running.

**Best for**: Tech-savvy users, Raspberry Pi enthusiasts, or anyone with a computer that stays on 24/7.

## Prerequisites

- Computer running Windows, macOS, or Linux
- Python 3.8 or higher
- Internet connection
- All API keys set up (see [API Setup Guides](../api-setup/))

## Installation Steps

### Step 1: Install Python

**Windows**:
1. Download Python from [python.org/downloads](https://python.org/downloads)
2. Run installer and **check "Add Python to PATH"**
3. Open Command Prompt and verify: `python --version`

**macOS**:
1. Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Install Python: `brew install python`
3. Verify: `python3 --version`

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3 python3-pip git
python3 --version
```

### Step 2: Download the Project

**Option A: Download ZIP**:
1. Go to your project's GitHub page
2. Click "Code" → "Download ZIP"
3. Extract to a folder like `C:\hobby-bot\` or `~/hobby-bot/`

**Option B: Git Clone** (if you have git):
```bash
git clone <your-repo-url> hobby-bot
cd hobby-bot
```

### Step 3: Install Dependencies

Navigate to your project folder and install requirements:

**Windows**:
```cmd
cd C:\hobby-bot
pip install -r requirements.txt
```

**macOS/Linux**:
```bash
cd ~/hobby-bot
pip3 install -r requirements.txt
```

### Step 4: Set Up Environment

1. **Copy environment template**:
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux  
   cp .env.example .env
   ```

2. **Edit your .env file** with your API keys:
   ```env
   YOUTUBE_API_KEY=your_actual_youtube_key
   ANTHROPIC_API_KEY=your_actual_anthropic_key
   DISCORD_BOT_TOKEN=your_actual_bot_token
   DISCORD_CHANNEL_ID=123456789012345678
   DISCORD_USER_ID=987654321098765432
   GOOGLE_SHEETS_ID=your_actual_sheet_id
   GOOGLE_SERVICE_ACCOUNT_FILE=auth/hobbymaxxxing-service-account.json
   ```

3. **Move your Google Service Account file** to `auth/hobbymaxxxing-service-account.json`

### Step 5: Test the Bot

Test that everything works:
```bash
python main.py --help
```

You should see the help menu with different modes.

## Running Options

### Option 1: Manual Daily Run (Simplest)

Run once per day manually:
```bash
python main.py --daily-job
```

This will:
- Find a video recommendation
- Post it to Discord  
- Exit cleanly

### Option 2: Persistent Listener (24/7)

Run the bot continuously:
```bash
python main.py --listen
```

This keeps the bot online to:
- Listen for reactions on videos
- Handle topic exploration messages
- Record feedback to Google Sheets

### Option 3: Complete Workflow (Testing)

Run the full workflow once:
```bash
python main.py
```

This will:
- Post a video recommendation
- Wait for your feedback and notes
- Exit after notes are collected

## Automation (Optional)

### Windows: Task Scheduler

1. **Open Task Scheduler**: Start Menu → "Task Scheduler"
2. **Create Basic Task**:
   - Name: `Hobby Bot Daily`
   - Trigger: Daily at 9:00 AM
   - Action: Start a program
   - Program: `python`
   - Arguments: `main.py --daily-job`
   - Start in: `C:\path\to\hobby-bot`

### macOS/Linux: Cron Jobs

1. **Edit crontab**:
   ```bash
   crontab -e
   ```

2. **Add daily job** (9 AM every day):
   ```cron
   0 9 * * * cd /path/to/hobby-bot && python3 main.py --daily-job >> /var/log/hobby-bot.log 2>&1
   ```

3. **Save and exit** (Ctrl+X, then Y, then Enter)

### Running Persistent Listener as Background Service

**Windows (using NSSM)**:
1. Download NSSM from [nssm.cc](https://nssm.cc)
2. Install service:
   ```cmd
   nssm install HobbyBot python C:\hobby-bot\main.py --listen
   nssm set HobbyBot AppDirectory C:\hobby-bot
   nssm start HobbyBot
   ```

**macOS/Linux (using systemd)**:
1. Copy service file:
   ```bash
   sudo cp config/hobby-listener.service /etc/systemd/system/
   ```
2. Edit paths in service file:
   ```bash
   sudo nano /etc/systemd/system/hobby-listener.service
   # Update paths to match your installation
   ```
3. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable hobby-listener
   sudo systemctl start hobby-listener
   ```

## Monitoring

**Check if bot is running**:
```bash
# Linux/macOS
ps aux | grep python

# Windows  
tasklist | findstr python
```

**View logs**:
```bash
# If using systemd
sudo journalctl -u hobby-listener -f

# If using cron
tail -f /var/log/hobby-bot.log

# Windows Event Viewer for services
```

## Troubleshooting

**❌ "Python not found" error**:
- Reinstall Python with "Add to PATH" checked (Windows)
- Use `python3` instead of `python` (macOS/Linux)

**❌ "Permission denied" error**:
- Check file permissions: `chmod +x main.py`
- Run with administrator/sudo if needed (not recommended long-term)

**❌ "Module not found" error**:
- Make sure you're in the right directory
- Reinstall dependencies: `pip install -r requirements.txt`

**❌ Bot stops working after computer restart**:
- Set up automatic startup (systemd service or Windows service)
- Add the bot to your startup programs

**Need help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) for more solutions.