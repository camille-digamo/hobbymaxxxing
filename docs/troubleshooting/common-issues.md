# Troubleshooting Guide

## Quick Diagnostics

### Test Each Component Separately

**1. Test Environment Loading**:
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('✅ Environment loaded')
print('YouTube API:', '✅' if os.getenv('YOUTUBE_API_KEY') else '❌')
print('Anthropic API:', '✅' if os.getenv('ANTHROPIC_API_KEY') else '❌')  
print('Discord Token:', '✅' if os.getenv('DISCORD_BOT_TOKEN') else '❌')
print('Google Sheets:', '✅' if os.getenv('GOOGLE_SHEETS_ID') else '❌')
"
```

**2. Test Google Sheets Connection**:
```bash
python -c "
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
load_dotenv()

try:
    credentials = Credentials.from_service_account_file(
        os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE'),
        scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(os.getenv('GOOGLE_SHEETS_ID'))
    print('✅ Google Sheets connection successful')
except Exception as e:
    print(f'❌ Google Sheets error: {e}')
"
```

**3. Test Discord Connection**:
```bash
python -c "
import discord
import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Discord connection successful: {client.user}')
    await client.close()

try:
    client.run(os.getenv('DISCORD_BOT_TOKEN'))
except Exception as e:
    print(f'❌ Discord error: {e}')
"
```

## Common Errors and Solutions

### Environment and Configuration Issues

**❌ "No module named 'dotenv'"**
```bash
# Solution: Install python-dotenv
pip install python-dotenv
# Or reinstall all requirements
pip install -r requirements.txt
```

**❌ ".env file not found"**
```bash
# Check if .env exists
ls -la .env

# If missing, copy from template
cp .env.example .env
# Then edit .env with your actual values
```

**❌ "Invalid API key format"**
- **YouTube API key**: Should start with `AIza` and be ~40 characters
- **Anthropic API key**: Should start with `sk-ant-api03` and be very long (~100+ characters)
- **Discord token**: Should be ~60 characters with dots (format: `XXX.YYY.ZZZ`)
- **Check for extra spaces** before/after keys

### Discord Bot Issues

**❌ "Bot not responding to messages"**
1. **Check Message Content Intent**:
   - Go to Discord Developer Portal → Your App → Bot
   - Enable "Message Content Intent"
   - Restart your bot

2. **Check Bot Permissions**:
   - Right-click your Discord channel → Edit Channel → Permissions
   - Ensure bot role has: Send Messages, Read Messages, Add Reactions

3. **Verify Channel ID**:
   ```bash
   # Test if channel ID is correct
   python -c "
   import os
   from dotenv import load_dotenv
   load_dotenv()
   channel_id = os.getenv('DISCORD_CHANNEL_ID')
   print(f'Channel ID: {channel_id}')
   print(f'Is numeric: {channel_id.isdigit()}')
   print(f'Length: {len(channel_id)} (should be 17-19 digits)')
   "
   ```

**❌ "403 Forbidden" Discord errors**
- Bot token is invalid or expired
- Bot lacks permissions in the channel
- Bot was removed from server

**❌ "Bot appears offline"**
- This is normal when bot isn't running
- Bot shows online only when `main.py` is actively running

### Google Sheets Issues  

**❌ "Service account not found"**
1. **Check file path**:
   ```bash
   ls -la auth/hobbymaxxxing-service-account.json
   # Should show the file exists
   ```

2. **Verify file content**:
   ```bash
   head -5 auth/hobbymaxxxing-service-account.json
   # Should show JSON starting with {"type": "service_account"
   ```

3. **Check sheet sharing**:
   - Open your Google Sheet
   - Click "Share" → ensure service account email is listed with Editor access
   - Service account email is in the JSON file under `"client_email"`

**❌ "Permission denied" for Google Sheets**
```bash
# Check service account email
python -c "
import json
with open('auth/hobbymaxxxing-service-account.json') as f:
    data = json.load(f)
print(f'Service account email: {data[\"client_email\"]}')
print('Make sure this email has Editor access to your sheet!')
"
```

**❌ "Sheet not found" errors**
- Verify Google Sheets ID in `.env` file
- Sheet ID is the long string in your sheet URL between `/d/` and `/edit`
- Make sure sheet has `topics` and `videos` worksheets with correct headers

### API Issues

**❌ "YouTube API quota exceeded"**
- Free tier: 10,000 requests/day
- Bot uses ~3-5 requests per recommendation
- Monitor usage at [console.developers.google.com](https://console.developers.google.com)
- Consider upgrading if hitting limits frequently

**❌ "Anthropic API rate limits"**
- Free tier has lower rate limits
- Bot has built-in delays to prevent this
- Add payment method for higher limits

**❌ "Invalid YouTube API response"**
```bash
# Test YouTube API directly
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
import requests

api_key = os.getenv('YOUTUBE_API_KEY')
url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q=python+tutorial&key={api_key}'
response = requests.get(url)
print(f'Status: {response.status_code}')
if response.status_code != 200:
    print(f'Error: {response.text}')
else:
    print('✅ YouTube API working')
"
```

### Deployment-Specific Issues

### Local Deployment

**❌ "python command not found"**
- Windows: Reinstall Python with "Add to PATH" checked
- macOS/Linux: Use `python3` instead of `python`
- Install via package manager: `brew install python` or `sudo apt install python3`

**❌ "Permission denied" on Linux/macOS**
```bash
# Fix file permissions
chmod +x main.py
# Or run with python explicitly
python3 main.py
```

**❌ Cron job not running**
```bash
# Check cron service
sudo systemctl status cron  # Linux
sudo launchctl list | grep cron  # macOS

# Check cron logs
grep CRON /var/log/syslog  # Linux  
tail -f /var/log/cron.log  # Some systems

# Test cron entry manually
cd /path/to/hobbymaxxxing && python3 main.py --daily-job
```

### GitHub Actions Issues

**❌ Workflow not running**
1. Check if Actions are enabled: Repository → Settings → Actions → Allow all actions
2. Verify workflow file location: `.github/workflows/daily-hobby.yml`
3. Check workflow syntax: Actions tab will show syntax errors

**❌ "Secret not found" in Actions**
- Go to Repository → Settings → Secrets and variables → Actions
- Verify all required secrets are added
- Secret names must match exactly (case-sensitive)

**❌ Google Service Account JSON issues in Actions**
- Make sure `GOOGLE_SERVICE_ACCOUNT_JSON` contains the **entire JSON file content**
- Include the opening `{` and closing `}`
- No line breaks or formatting changes

### Railway Issues

**❌ Deployment failing**
```bash
# Check Railway logs
railway logs --tail

# Common issues:
# 1. Missing environment variables
# 2. Build failing due to Python version
# 3. Port binding issues (Railway handles this automatically)
```

**❌ "Service not responding"**
- Railway free tier has sleep timeouts
- Upgrade to Hobby plan ($5/month) for always-on service
- Check if service restarted due to crashes

### Raspberry Pi Issues

**❌ "Memory issues" / Bot crashes**
```bash
# Check memory usage
free -h

# Check swap
sudo dphys-swapfile swapon

# Consider using Pi 4 with more RAM
```

**❌ "SSL certificate errors"**
```bash
# Update certificates
sudo apt update && sudo apt install ca-certificates

# Update system time (important for SSL)
sudo ntpdate -s time.nist.gov
```

**❌ "WiFi keeps disconnecting"**
```bash
# Disable WiFi power management
sudo nano /etc/rc.local
# Add before 'exit 0': /sbin/iwconfig wlan0 power off
```

## Performance Optimization

### Reduce Startup Time
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Memory Optimization
- Use `--daily-job` mode for scheduled runs (uses less memory)
- Restart listener service weekly: `sudo systemctl restart hobby-listener`
- Monitor memory with `htop` or `top`

### Network Issues
```bash
# Test internet connectivity
ping google.com

# Test DNS resolution
nslookup discord.com

# Check if ports are blocked (rare)
telnet discord.com 443
```

## Getting Help

### Enable Debug Logging

Add to your `.env` file:
```env
DEBUG=true
```

This will show more detailed error messages.

### Collect Debug Information

Run this script to collect system info:
```bash
python -c "
import sys, os, platform
from dotenv import load_dotenv
load_dotenv()

print('=== System Info ===')
print(f'Python: {sys.version}')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Architecture: {platform.machine()}')

print('\n=== Environment Check ===')
env_vars = ['YOUTUBE_API_KEY', 'ANTHROPIC_API_KEY', 'DISCORD_BOT_TOKEN', 'DISCORD_CHANNEL_ID', 'DISCORD_USER_ID', 'GOOGLE_SHEETS_ID', 'GOOGLE_SERVICE_ACCOUNT_FILE']
for var in env_vars:
    value = os.getenv(var)
    if value:
        # Show first/last 4 chars for security
        if len(value) > 8:
            masked = value[:4] + '...' + value[-4:]
        else:
            masked = '***'
        print(f'{var}: {masked}')
    else:
        print(f'{var}: ❌ Missing')

print('\n=== Files Check ===')
files = ['main.py', 'requirements.txt', '.env']
for file in files:
    exists = '✅' if os.path.exists(file) else '❌'
    print(f'{file}: {exists}')
"
```

### Support Resources

1. **Check logs first**: Always check error logs before asking for help
2. **Search existing issues**: Look for similar problems in GitHub issues
3. **Provide details**: Include error messages, system info, and steps to reproduce
4. **Test components separately**: Use the diagnostic scripts above

**Remember**: Most issues are configuration-related. Double-check your API keys and file paths!