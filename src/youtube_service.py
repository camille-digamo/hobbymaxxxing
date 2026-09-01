"""
YouTube API integration for video search and management
"""

from typing import List, Dict, Any
from .utils import YOUTUBE_API_KEY

# Robust import handling for Railway deployment
YOUTUBE_API_AVAILABLE = False
build = None

try:
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
    print("✅ YouTube API client loaded successfully")
except ImportError as e:
    print(f"⚠️  YouTube API client not available: {e}")
    YOUTUBE_API_AVAILABLE = False
    build = None
except Exception as e:
    print(f"⚠️  Error loading YouTube API client: {e}")
    YOUTUBE_API_AVAILABLE = False
    build = None


def search_youtube(topic: str, parent_topic: str = "", max_results: int = 8) -> List[Dict[str, Any]]:
    """Search YouTube for videos on the given topic."""
    # Enhance search query with parent topic for better targeting
    search_query = topic

    if parent_topic and parent_topic.lower() not in topic.lower():
        # Add parent topic to make search more specific
        search_query = f"{topic} {parent_topic}"

    print(f"🔍 Searching YouTube for: '{search_query}'...")

    # Comprehensive availability checks
    print(f"🔧 Debug: YOUTUBE_API_AVAILABLE={YOUTUBE_API_AVAILABLE}")
    print(f"🔧 Debug: build function={build}")
    print(f"🔧 Debug: API key available={'Yes' if YOUTUBE_API_KEY else 'No'}")

    if not YOUTUBE_API_AVAILABLE:
        print("❌ YouTube API not available - returning empty list")
        return []

    if not YOUTUBE_API_KEY:
        print("❌ YouTube API key not configured")
        return []

    # Wrap the entire API call in comprehensive error handling
    try:
        # Check if build function is available and callable
        if build is None:
            print("❌ YouTube API build function is None")
            return []

        if not callable(build):
            print("❌ YouTube API build function is not callable")
            return []

        print("🔧 Debug: About to call build() function")
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        print("🔧 Debug: build() call successful")

        # Search for videos
        search_response = youtube.search().list(
            q=search_query,
            part="snippet",
            type="video",
            maxResults=max_results,
            order="relevance"
        ).execute()

        videos = []
        for item in search_response["items"]:
            video = {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel_title": item["snippet"]["channelTitle"],
                "description": item["snippet"]["description"],
                "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
                "video_url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video)

        print(f"✅ Found {len(videos)} video results")
        return videos

    except NameError as e:
        print(f"❌ YouTube search NameError (missing import): {e}")
        print("This indicates missing google-api-python-client package on Railway")
        return []
    except Exception as e:
        print(f"❌ YouTube search error: {e}")
        return []


def filter_available_videos(all_videos: List[Dict[str, Any]], watched_videos: List[str]) -> List[Dict[str, Any]]:
    """Filter out videos that have already been watched."""
    available_videos = []

    for video in all_videos:
        video_url = video["video_url"]

        # Check against watched videos by URL
        if video_url not in watched_videos:
            available_videos.append(video)
        else:
            print(f"⏭️  Skipping already watched video: {video['title']}")

    print(f"✅ {len(available_videos)} new videos available (filtered from {len(all_videos)} total)")
    return available_videos