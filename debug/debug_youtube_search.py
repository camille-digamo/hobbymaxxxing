#!/usr/bin/env python3
"""
YouTube Search Debugging Tool
=============================
Test YouTube API searches locally to debug video search issues.

Usage:
    python debug_youtube_search.py "beginner kayaking"
    python debug_youtube_search.py "food history" "cooking"
"""

import sys
import os
sys.path.append('.')

from main import search_youtube, YOUTUBE_API_KEY

def debug_search(topic, parent_topic=None, max_results=8):
    """Debug YouTube search with detailed output."""
    print("=" * 60)
    print("🔍 YOUTUBE SEARCH DEBUG TOOL")
    print("=" * 60)
    print()

    # Check API key
    print(f"📋 API Key Status: {'✅ Available' if YOUTUBE_API_KEY else '❌ Missing'}")
    if not YOUTUBE_API_KEY:
        print("   Set YOUTUBE_API_KEY in your .env file")
        return False
    print()

    # Search parameters
    print("📝 Search Parameters:")
    print(f"   Topic: '{topic}'")
    if parent_topic:
        print(f"   Parent Topic: '{parent_topic}'")
        search_query = f"{topic} {parent_topic}" if parent_topic.lower() not in topic.lower() else topic
    else:
        search_query = topic
        print(f"   Parent Topic: None")
    print(f"   Final Query: '{search_query}'")
    print(f"   Max Results: {max_results}")
    print()

    try:
        # Perform search
        print("🔍 Performing YouTube Search...")
        results = search_youtube(topic, parent_topic or "", max_results)
        print()

        # Results summary
        print("📊 SEARCH RESULTS:")
        print(f"   Videos Found: {len(results)}")
        print()

        if results:
            print("📺 VIDEO DETAILS:")
            for i, video in enumerate(results, 1):
                print(f"{i}. 📹 {video['title']}")
                print(f"   👤 Channel: {video['channel_title']}")
                print(f"   🔗 URL: {video['video_url']}")
                print(f"   📝 Description: {video['description'][:100]}...")
                print()
        else:
            print("❌ NO VIDEOS FOUND")
            print()
            print("🔧 TROUBLESHOOTING TIPS:")
            print("   1. Try a more general search term")
            print("   2. Check for typos in the topic")
            print("   3. Verify YouTube API quotas aren't exceeded")
            print("   4. Test the same search on YouTube.com manually")

        return len(results) > 0

    except Exception as e:
        print(f"❌ SEARCH ERROR: {e}")
        print()
        print("🔧 COMMON ERROR CAUSES:")
        print("   1. Invalid YouTube API key")
        print("   2. API quota exceeded")
        print("   3. Network connectivity issues")
        print("   4. YouTube API service disruption")

        import traceback
        print("\n🐛 FULL ERROR TRACE:")
        traceback.print_exc()

        return False

def main():
    """Main entry point for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python debug_youtube_search.py <topic> [parent_topic]")
        print()
        print("Examples:")
        print("  python debug_youtube_search.py 'beginner kayaking'")
        print("  python debug_youtube_search.py 'food history' 'cooking'")
        print("  python debug_youtube_search.py 'guitar techniques' 'music'")
        sys.exit(1)

    topic = sys.argv[1]
    parent_topic = sys.argv[2] if len(sys.argv) > 2 else None

    success = debug_search(topic, parent_topic)

    print("=" * 60)
    if success:
        print("✅ SEARCH SUCCESSFUL - Videos found!")
    else:
        print("❌ SEARCH FAILED - No videos found or error occurred")
    print("=" * 60)

if __name__ == "__main__":
    main()