# Raspberry Pi Setup Guide

## Overview

Running the Hobby Maxxxer on a Raspberry Pi is perfect for a dedicated, always-on bot that costs **$0/month** to operate after the initial Pi purchase (~$35-75).

**Best for**: Makers, tinkerers, or anyone who wants a dedicated hobby bot device.

## Prerequisites

- Raspberry Pi 3B+ or newer (Raspberry Pi 4 recommended)
- MicroSD card (16GB+, Class 10)
- Stable internet connection (WiFi or Ethernet)
- All API keys set up (see [API Setup Guides](../api-setup/))

## Step 1: Set Up Raspberry Pi OS

### Option A: Pre-built Image (Easiest)
1. **Download Raspberry Pi Imager**: [rpi.org/software](https://rpi.org/software)
2. **Flash SD card**:
   - Choose "Raspberry Pi OS Lite" (no desktop needed)
   - Enable SSH and set username/password
   - Configure WiFi if needed
3. **Boot Pi and SSH in**:
   ```bash
   ssh pi@raspberrypi.local
   ```

### Option B: Existing Pi
If you already have a Pi running:
```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Dependencies

```bash
# Install Python and Git
sudo apt install python3-pip python3-venv git -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev -y
```

## Step 3: Download and Set Up Project

```bash
# Create directory and clone
cd ~
git clone <your-repo-url> hobbymaxxxing
cd hobbymaxxxing

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

Fill in your API keys:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=123456789012345678
DISCORD_USER_ID=987654321098765432
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_SERVICE_ACCOUNT_FILE=/home/pi/hobbymaxxxing/auth/hobbymaxxxing-service-account.json
```

## Step 5: Upload Service Account File

**Option A: SCP from your computer**:
```bash
# From your computer (not the Pi)
scp hobbymaxxxing-service-account.json pi@raspberrypi.local:~/hobbymaxxxing/auth/
```

**Option B: Copy-paste method**:
```bash
# On the Pi
nano auth/hobbymaxxxing-service-account.json
# Paste the JSON content and save (Ctrl+X, Y, Enter)
```

## Step 6: Test the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Test basic functionality
python main.py --help

# Test a daily job
python main.py --daily-job
```

Check Discord - you should see a video recommendation!

## Step 7: Set Up Automation

### Install Systemd Service (Persistent Listener)

```bash
# Edit service file to match your paths
sudo nano /etc/systemd/system/hobby-listener.service
```

Update paths in the service file:
```ini
[Unit]
Description=YouTube Hobby Maxxxer Listener
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/hobbymaxxxing
ExecStart=/home/pi/hobbymaxxxing/venv/bin/python /home/pi/hobbymaxxxing/main.py --listen
Restart=on-failure
RestartSec=5
EnvironmentFile=/home/pi/hobbymaxxxing/.env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hobby-listener

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hobby-listener
sudo systemctl start hobby-listener
```

### Set Up Daily Cron Job

```bash
# Edit crontab
crontab -e

# Add daily job (9 AM every day)
0 9 * * * cd /home/pi/hobbymaxxxing && /home/pi/hobbymaxxxing/venv/bin/python main.py --daily-job >> /var/log/hobby-bot.log 2>&1
```

## Step 8: Monitor and Maintain

### Check Service Status
```bash
# Check if listener is running
sudo systemctl status hobby-listener

# View live logs
sudo journalctl -u hobby-listener -f

# Restart service if needed
sudo systemctl restart hobby-listener
```

### Check Daily Job
```bash
# View cron logs
tail -f /var/log/hobby-bot.log

# Test daily job manually
cd ~/hobbymaxxxing && python main.py --daily-job
```

### Monitor System Resources
```bash
# Check CPU and memory usage
htop

# Check disk space
df -h

# Check temperature (important for Pi 4)
vcgencmd measure_temp
```

## Optional: Remote Access Setup

### Set Up Dynamic DNS (if no static IP)
```bash
# Install ddclient for dynamic DNS
sudo apt install ddclient

# Configure with your DNS provider (No-IP, DuckDNS, etc.)
```

### Set Up VPN Access (Advanced)
```bash
# Install WireGuard for secure remote access
sudo apt install wireguard

# Configure VPN (follow provider-specific guides)
```

## Troubleshooting

**❌ "Permission denied" errors**:
```bash
# Fix file permissions
sudo chown -R pi:pi /home/pi/hobbymaxxxing
chmod +x main.py
```

**❌ Service won't start**:
```bash
# Check service logs
sudo journalctl -u hobby-listener --no-pager

# Verify virtual environment works
source venv/bin/activate && python --version
```

**❌ Cron job not running**:
```bash
# Check cron service
sudo systemctl status cron

# View cron logs
grep CRON /var/log/syslog | tail -20
```

**❌ Bot goes offline randomly**:
```bash
# Check for memory issues
free -h

# Check for overheating (Pi 4)
vcgencmd measure_temp

# Consider adding a heat sink or fan
```

**❌ WiFi keeps disconnecting**:
```bash
# Edit WiFi power management
sudo nano /etc/rc.local

# Add before "exit 0":
# /sbin/iwconfig wlan0 power off
```

## Pi-Specific Optimizations

### Reduce SD Card Wear
```bash
# Move logs to RAM (tmpfs)
sudo nano /etc/fstab

# Add:
# tmpfs /var/log tmpfs defaults,noatime,nosuid,mode=0755,size=100m 0 0
```

### Automatic Updates
```bash
# Install unattended upgrades
sudo apt install unattended-upgrades

sudo dpkg-reconfigure -plow unattended-upgrades
```

### Temperature Monitoring
```bash
# Add temperature check to daily job
# Edit crontab and add:
# 0 12 * * * vcgencmd measure_temp | logger -t pi-temp
```

## Backup Strategy

```bash
# Create backup script
nano ~/backup-hobby-bot.sh

# Add:
#!/bin/bash
tar -czf ~/hobby-backup-$(date +%Y%m%d).tar.gz \
  ~/hobbymaxxxing/.env \
  ~/hobbymaxxxing/auth/ \
  /etc/systemd/system/hobby-listener.service

# Make executable
chmod +x ~/backup-hobby-bot.sh

# Run weekly via cron
# 0 2 * * 0 ~/backup-hobby-bot.sh
```

**Total Cost**: ~$35-75 one-time for Pi + MicroSD + Power Supply + Case

**Need help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) for more solutions.