#!/usr/bin/env python3
"""
Railway Runtime Import Test
===========================
Test if runtime imports work on Railway to fix the "name 'build' is not defined" issue.
"""

import sys
import os

def test_runtime_imports():
    print("🧪 TESTING RAILWAY RUNTIME IMPORTS")
    print("=" * 50)

    # Test environment
    if os.getenv("RAILWAY_ENVIRONMENT"):
        print("🚂 Running on Railway")
    else:
        print("💻 Running locally")

    print(f"🐍 Python: {sys.version}")
    print()

    # Test YouTube API runtime import
    print("📺 Testing YouTube API Runtime Import...")
    try:
        from googleapiclient.discovery import build as runtime_build
        print("✅ Runtime import successful")

        # Test client creation
        api_key = os.getenv("YOUTUBE_API_KEY")
        if api_key:
            try:
                youtube = runtime_build("youtube", "v3", developerKey=api_key)
                print("✅ YouTube client created successfully")

                # Test actual search
                response = youtube.search().list(
                    q="test search",
                    part="snippet",
                    type="video",
                    maxResults=1
                ).execute()

                if response.get("items"):
                    print(f"✅ YouTube search successful: found {len(response['items'])} results")
                else:
                    print("⚠️  YouTube search returned no results")

            except Exception as e:
                print(f"❌ YouTube client creation failed: {e}")
        else:
            print("⚠️  No YOUTUBE_API_KEY for full test")

    except ImportError as e:
        print(f"❌ YouTube runtime import failed: {e}")
    except Exception as e:
        print(f"❌ YouTube test error: {e}")

    print()

    # Test Anthropic API runtime import
    print("🤖 Testing Anthropic API Runtime Import...")
    try:
        from anthropic import Anthropic as runtime_Anthropic
        print("✅ Runtime import successful")

        # Test client creation
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                client = runtime_Anthropic(api_key=api_key)
                print("✅ Anthropic client created successfully")

                # Test simple API call
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}]
                )

                if response and response.content:
                    print("✅ Anthropic API call successful")
                else:
                    print("⚠️  Anthropic API call returned no content")

            except Exception as e:
                print(f"❌ Anthropic client creation failed: {e}")
        else:
            print("⚠️  No ANTHROPIC_API_KEY for full test")

    except ImportError as e:
        print(f"❌ Anthropic runtime import failed: {e}")
    except Exception as e:
        print(f"❌ Anthropic test error: {e}")

    print()
    print("🔍 TESTING SERVICES...")

    # Test our service modules
    try:
        from src.youtube_service import search_youtube
        print("✅ YouTube service import successful")

        results = search_youtube("test topic")
        print(f"✅ YouTube service call returned {len(results)} results")

    except Exception as e:
        print(f"❌ YouTube service test failed: {e}")

    try:
        from src.claude_service import generate_topic_expansion
        print("✅ Claude service import successful")

        results = generate_topic_expansion("test topic", "test parent")
        print(f"✅ Claude service call returned {len(results)} topics")

    except Exception as e:
        print(f"❌ Claude service test failed: {e}")

    print()
    print("✅ RUNTIME IMPORT TEST COMPLETE!")

if __name__ == "__main__":
    test_runtime_imports()