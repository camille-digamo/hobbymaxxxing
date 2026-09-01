#!/usr/bin/env python3
"""
🔍 YouTube Hobby Maxxxer Setup Test
=====================================
Run this script to test your configuration and diagnose issues.

Usage: python test-setup.py
"""

import os
import sys
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def print_result(test, passed, details=""):
    status = "✅" if passed else "❌"
    print(f"{status} {test}")
    if details:
        print(f"   {details}")

def test_python_version():
    print_header("Python Version Check")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_result(f"Python {version.major}.{version.minor}.{version.micro}", True, "Compatible version")
        return True
    else:
        print_result(f"Python {version.major}.{version.minor}.{version.micro}", False, "Need Python 3.8+")
        return False

def test_dependencies():
    print_header("Dependencies Check")
    required_packages = [
        'discord', 'anthropic', 'google-api-python-client',
        'python-dotenv', 'gspread', 'google-auth'
    ]

    all_good = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_result(package, True)
        except ImportError:
            print_result(package, False, f"Run: pip install {package}")
            all_good = False

    return all_good

def test_environment_files():
    print_header("Environment Files Check")

    # Check .env file
    env_exists = Path('.env').exists()
    print_result(".env file", env_exists, "Copy from .env.example if missing")

    # Check auth directory
    auth_dir = Path('auth').exists()
    print_result("auth/ directory", auth_dir, "Should contain your Google service account JSON")

    # Check Google service account file
    service_files = list(Path('auth').glob('*.json')) if auth_dir else []
    has_service_account = len(service_files) > 0
    print_result("Google service account JSON", has_service_account,
                f"Found: {', '.join(f.name for f in service_files) if service_files else 'None'}")

    return env_exists and auth_dir and has_service_account

def test_environment_variables():
    print_header("Environment Variables Check")

    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print_result("Loading .env", False, "Install python-dotenv")
        return False

    required_vars = {
        'YOUTUBE_API_KEY': 'Should start with AIza',
        'ANTHROPIC_API_KEY': 'Should start with sk-ant-api03',
        'DISCORD_BOT_TOKEN': 'Long token with dots (XXX.YYY.ZZZ)',
        'DISCORD_CHANNEL_ID': 'Numeric Discord channel ID',
        'DISCORD_USER_ID': 'Your numeric Discord user ID',
        'GOOGLE_SHEETS_ID': 'Google Sheets document ID',
        'GOOGLE_SERVICE_ACCOUNT_FILE': 'Path to JSON file in auth/ folder'
    }

    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if len(value) > 8:
                masked = f"{value[:4]}...{value[-4:]}"
            else:
                masked = "***"
            print_result(var, True, f"Set ({masked})")
        else:
            print_result(var, False, f"Missing - {description}")
            all_good = False

    return all_good

def test_google_sheets_connection():
    print_header("Google Sheets Connection Test")

    try:
        from dotenv import load_dotenv
        import gspread
        from google.oauth2.service_account import Credentials

        load_dotenv()

        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        sheets_id = os.getenv('GOOGLE_SHEETS_ID')

        if not service_account_file or not sheets_id:
            print_result("Google Sheets config", False, "Missing GOOGLE_SHEETS_ID or GOOGLE_SERVICE_ACCOUNT_FILE")
            return False

        if not os.path.exists(service_account_file):
            print_result("Service account file", False, f"File not found: {service_account_file}")
            return False

        # Test JSON file is valid
        with open(service_account_file) as f:
            service_account_data = json.load(f)

        client_email = service_account_data.get('client_email', 'Unknown')
        print_result("Service account JSON", True, f"Email: {client_email}")

        # Test connection
        credentials = Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://spreadsheets.google.com/feeds',
                   'https://www.googleapis.com/auth/drive']
        )

        client = gspread.authorize(credentials)
        sheet = client.open_by_key(sheets_id)

        print_result("Google Sheets connection", True, f"Connected to: {sheet.title}")

        # Check worksheets
        try:
            topics_sheet = sheet.worksheet('topics')
            print_result("'topics' worksheet", True)
        except:
            print_result("'topics' worksheet", False, "Create a worksheet named 'topics'")

        try:
            videos_sheet = sheet.worksheet('videos')
            print_result("'videos' worksheet", True)
        except:
            print_result("'videos' worksheet", False, "Create a worksheet named 'videos'")

        return True

    except Exception as e:
        print_result("Google Sheets connection", False, str(e))
        return False

def test_discord_connection():
    print_header("Discord Connection Test")

    try:
        from dotenv import load_dotenv
        import discord
        import asyncio

        load_dotenv()

        token = os.getenv('DISCORD_BOT_TOKEN')
        channel_id = os.getenv('DISCORD_CHANNEL_ID')
        user_id = os.getenv('DISCORD_USER_ID')

        if not token:
            print_result("Discord token", False, "DISCORD_BOT_TOKEN not set")
            return False

        if not channel_id or not channel_id.isdigit():
            print_result("Channel ID", False, "DISCORD_CHANNEL_ID must be numeric")
            return False

        if not user_id or not user_id.isdigit():
            print_result("User ID", False, "DISCORD_USER_ID must be numeric")
            return False

        # Test bot connection (quick test)
        async def test_bot():
            intents = discord.Intents.default()
            intents.message_content = True
            client = discord.Client(intents=intents)

            @client.event
            async def on_ready():
                print_result("Discord bot connection", True, f"Connected as: {client.user}")

                # Test channel access
                channel = client.get_channel(int(channel_id))
                if channel:
                    print_result("Channel access", True, f"Can access: {channel.name}")
                else:
                    print_result("Channel access", False, "Cannot access channel - check ID and permissions")

                await client.close()

            try:
                await client.start(token)
            except discord.LoginFailure:
                print_result("Discord bot connection", False, "Invalid bot token")
            except Exception as e:
                print_result("Discord bot connection", False, str(e))

        # Run test with timeout
        try:
            asyncio.run(asyncio.wait_for(test_bot(), timeout=10))
            return True
        except asyncio.TimeoutError:
            print_result("Discord connection", False, "Connection timeout - check network")
            return False

    except Exception as e:
        print_result("Discord setup", False, str(e))
        return False

def test_youtube_api():
    print_header("YouTube API Test")

    try:
        from dotenv import load_dotenv
        from googleapiclient.discovery import build

        load_dotenv()

        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            print_result("YouTube API key", False, "YOUTUBE_API_KEY not set")
            return False

        youtube = build('youtube', 'v3', developerKey=api_key)

        # Test search
        request = youtube.search().list(
            part='snippet',
            q='python tutorial',
            maxResults=1,
            type='video'
        )

        response = request.execute()

        if response.get('items'):
            print_result("YouTube API connection", True, "Successfully searched videos")
            return True
        else:
            print_result("YouTube API connection", False, "No search results returned")
            return False

    except Exception as e:
        print_result("YouTube API", False, str(e))
        return False

def test_anthropic_api():
    print_header("Anthropic API Test")

    try:
        from dotenv import load_dotenv
        from anthropic import Anthropic

        load_dotenv()

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print_result("Anthropic API key", False, "ANTHROPIC_API_KEY not set")
            return False

        client = Anthropic(api_key=api_key)

        # Test simple request
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'test'"}]
        )

        if message.content and message.content[0].text.strip().lower() == 'test':
            print_result("Anthropic API connection", True, "Successfully connected to Claude")
            return True
        else:
            print_result("Anthropic API connection", True, "Connected but unexpected response")
            return True

    except Exception as e:
        print_result("Anthropic API", False, str(e))
        return False

def main():
    print("🎯 YouTube Hobby Maxxxer Setup Test")
    print("====================================")
    print("This will test your configuration and diagnose common issues.")
    print("Make sure you've completed the API setup guides first!")

    # Run all tests
    tests = [
        test_python_version,
        test_dependencies,
        test_environment_files,
        test_environment_variables,
        test_google_sheets_connection,
        test_discord_connection,
        test_youtube_api,
        test_anthropic_api
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)

    # Final summary
    print_header("Final Summary")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print("🎉 All tests passed! Your setup looks good.")
        print("\nNext steps:")
        print("• Run: python main.py --daily-job (test video recommendation)")
        print("• Run: python main.py --listen (start persistent bot)")
        print("• Check: docs/deployment/ for automation setup")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Check the failures above.")
        print("\nRecommended fixes:")
        print("• Review the API setup guides: docs/api-setup/")
        print("• Check the troubleshooting guide: docs/troubleshooting/common-issues.md")
        print("• Ensure all environment variables are set in .env")
        print("• Verify API keys are valid and have correct permissions")

if __name__ == "__main__":
    main()