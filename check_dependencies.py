#!/usr/bin/env python3
"""
Dependency Check Script
======================
Verify all required packages are installed and importable.
Use this to debug Railway deployment issues.

Usage: python3 check_dependencies.py
"""

import sys
import os

def check_import(package_name, import_statement):
    """Check if a package can be imported."""
    try:
        exec(import_statement)
        print(f"✅ {package_name}: Available")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: MISSING - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {package_name}: Available but error - {e}")
        return True  # Package exists but has issues

def main():
    print("🔍 DEPENDENCY CHECK")
    print("=" * 40)

    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"🐍 Python Version: {python_version}")

    # Check environment
    if os.getenv("RAILWAY_ENVIRONMENT"):
        print("🚂 Environment: Railway")
    else:
        print("💻 Environment: Local")

    print()
    print("📦 PACKAGE CHECK")
    print("-" * 40)

    # Core dependencies
    dependencies = [
        ("Discord.py", "import discord"),
        ("Google API Client", "from googleapiclient.discovery import build"),
        ("Google Auth", "from google.oauth2.service_account import Credentials"),
        ("Anthropic", "from anthropic import Anthropic"),
        ("Google Sheets", "import gspread"),
        ("Python Dotenv", "from dotenv import load_dotenv"),
        ("Requests", "import requests"),
    ]

    success_count = 0
    total_count = len(dependencies)

    for name, import_stmt in dependencies:
        if check_import(name, import_stmt):
            success_count += 1

    print()
    print("🧪 MODULE CHECK")
    print("-" * 40)

    # Check our custom modules
    custom_modules = [
        ("Utils", "from src.utils import YOUTUBE_API_KEY"),
        ("YouTube Service", "from src.youtube_service import search_youtube"),
        ("Claude Service", "from src.claude_service import get_claude_recommendation"),
        ("Sheets Service", "from src.sheets_service import get_google_sheets_client"),
        ("Discord Service", "from src.discord_service import detect_video_request_pattern"),
        ("Bot Class", "from src.bot import HobbyMaxxingBot"),
    ]

    module_success = 0
    module_total = len(custom_modules)

    for name, import_stmt in custom_modules:
        if check_import(name, import_stmt):
            module_success += 1

    print()
    print("📋 SUMMARY")
    print("=" * 40)
    print(f"Core Dependencies: {success_count}/{total_count} available")
    print(f"Custom Modules: {module_success}/{module_total} available")

    if success_count == total_count and module_success == module_total:
        print("🎉 ALL DEPENDENCIES AVAILABLE!")
        print("If the bot is still failing, check API keys and network connectivity.")
        return True
    else:
        print("❌ MISSING DEPENDENCIES DETECTED!")
        print("Install missing packages with: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)