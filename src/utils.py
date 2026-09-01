"""
Utilities and configuration for YouTube Hobby Maxxxer
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration constants
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID")) if os.getenv("DISCORD_CHANNEL_ID") else None
DISCORD_USER_ID = int(os.getenv("DISCORD_USER_ID")) if os.getenv("DISCORD_USER_ID") else None
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# Constants
DATE_FORMAT = '%Y/%m/%d'
FEEDBACK_EMOJIS = {
    '👍': 'liked',
    '👎': 'didn\'t_like',
    '❤️': 'loved',
    '💤': 'boring'
}

def validate_environment():
    """Check that all required environment variables are set."""
    missing = []

    if not YOUTUBE_API_KEY:
        missing.append("YOUTUBE_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not DISCORD_BOT_TOKEN:
        missing.append("DISCORD_BOT_TOKEN")
    if not DISCORD_CHANNEL_ID:
        missing.append("DISCORD_CHANNEL_ID")
    if not DISCORD_USER_ID:
        missing.append("DISCORD_USER_ID")
    if not GOOGLE_SHEETS_ID:
        missing.append("GOOGLE_SHEETS_ID")
    # Check Google service account credentials
    has_file = GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE)
    has_json = GOOGLE_SERVICE_ACCOUNT_JSON
    if not has_file and not has_json:
        missing.append("GOOGLE_SERVICE_ACCOUNT_FILE (with existing file) or GOOGLE_SERVICE_ACCOUNT_JSON")

    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please check your .env file and compare with .env.example")
        sys.exit(1)

def get_current_date():
    """Get current date in the standard format."""
    return datetime.now().strftime(DATE_FORMAT)