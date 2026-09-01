"""
Google Sheets API integration for data persistence
"""

import gspread
import json
import sys
import os
import time
from google.oauth2.service_account import Credentials
from typing import List, Tuple, Dict, Any
from .utils import (
    GOOGLE_SHEETS_ID,
    get_current_date
)

# Global client cache to avoid repeated authentication
_sheets_client = None


def get_google_sheets_client():
    """Initialize and return cached Google Sheets client."""
    global _sheets_client

    # Return cached client if available
    if _sheets_client is not None:
        return _sheets_client

    try:
        # Import credentials config only when needed to avoid module-level import issues
        from .utils import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SERVICE_ACCOUNT_JSON

        # Define the scope for Google Sheets API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # Load credentials from service account file or JSON content
        if GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
            # Use file path method (local development)
            print(f"🔑 Using Google service account file: {GOOGLE_SERVICE_ACCOUNT_FILE}")
            creds = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scope)
        elif GOOGLE_SERVICE_ACCOUNT_JSON:
            # Use JSON content method (GitHub Actions, Railway)
            print("🔑 Using Google service account JSON content")
            service_account_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
            creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        else:
            raise ValueError("No Google service account credentials found - need either GOOGLE_SERVICE_ACCOUNT_FILE (with existing file) or GOOGLE_SERVICE_ACCOUNT_JSON")

        # Create gspread client and cache it
        _sheets_client = gspread.authorize(creds)
        print("✅ Google Sheets client initialized and cached")

        return _sheets_client
    except Exception as e:
        print(f"❌ Failed to initialize Google Sheets client: {e}")
        print("⚠️  Google Sheets operations will not work until this is resolved")
        raise  # Re-raise the exception instead of exiting


def retry_on_quota_exceeded(func, max_retries=3):
    """Retry function with exponential backoff on quota exceeded errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e) or "quota exceeded" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5  # 5, 10, 20 seconds
                    print(f"⏱️  Rate limit hit, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Max retries ({max_retries}) exceeded for rate limiting")
                    raise
            else:
                # Not a rate limit error, re-raise immediately
                raise


def get_next_topic() -> Tuple[str, str, int]:
    """Get the next topic to recommend using smart selection algorithm."""
    print("📊 Smart topic selection from Google Sheets...")

    try:
        def _get_topic_data():
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            topics_worksheet = sheet.worksheet('topics')
            return topics_worksheet.get_all_records()

        # Get all topics data with retry logic
        topics_data = retry_on_quota_exceeded(_get_topic_data)

        if not topics_data:
            print("❌ No topics found in Google Sheets")
            return "general learning", "", 2

        # Calculate interest scores for each topic
        print("🧠 Calculating topic interest scores...")
        topic_weights = {}
        total_weight = 0

        for i, topic_row in enumerate(topics_data, start=2):  # Start at row 2 (header is row 1)
            topic = topic_row.get('topic', '')
            parent_topic = topic_row.get('parent_topic', '')
            last_watched = topic_row.get('last_watched', '')
            videos_watched = int(topic_row.get('videos_watched', 0))
            interest_score = float(topic_row.get('interest_score', 0))

            # Skip empty topics
            if not topic:
                continue

            # Calculate weight based on multiple factors
            weight = 1.0

            # Boost unwatched topics significantly
            if videos_watched == 0:
                weight *= 15  # 15x boost for completely unwatched topics
                print(f"🆕 Unwatched topic boost: {topic}")
            else:
                # Boost based on interest score (capped to prevent dominance)
                if interest_score > 0:
                    boost = min(interest_score, 3.0)  # Cap at 3x boost
                    weight *= boost
                    print(f"❤️ Interest boost for {topic}: {boost:.2f} (reduced)")

            topic_weights[(topic, parent_topic, i)] = weight
            total_weight += weight

        print(f"✅ Calculated interest scores for {len(topic_weights)} topics")

        if not topic_weights:
            print("❌ No valid topics found")
            return "general learning", "", 2

        # Weighted random selection
        import random
        random_value = random.random() * total_weight
        current_weight = 0

        for (topic, parent_topic, row), weight in topic_weights.items():
            current_weight += weight
            if random_value <= current_weight:
                print(f"🎯 Smart selection: '{topic}' (parent: {parent_topic}) [weight: {weight:.2f}]")
                print(f"📊 Selection from {len(topic_weights)} candidates (total weight: {total_weight:.2f})")
                return topic, parent_topic, row

        # Fallback (shouldn't reach here)
        topic_info = list(topic_weights.keys())[0]
        return topic_info[0], topic_info[1], topic_info[2]

    except Exception as e:
        print(f"❌ Error getting next topic: {e}")
        return "general learning", "", 2


def get_watched_videos() -> List[str]:
    """Get list of watched video URLs to avoid duplicates."""
    print("📖 Reading existing videos from Google Sheets...")

    try:
        def _get_videos_data():
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            videos_worksheet = sheet.worksheet('videos')
            return videos_worksheet.get_all_records()

        # Get all video records with retry logic
        videos_data = retry_on_quota_exceeded(_get_videos_data)
        watched_urls = []

        for video_row in videos_data:
            video_url = video_row.get('video_url', '')
            if video_url:
                watched_urls.append(video_url)

        print(f"✅ Found {len(videos_data)} videos in history ({len([v for v in videos_data if v.get('date_watched')])} watched)")
        return watched_urls

    except Exception as e:
        print(f"❌ Error reading watched videos: {e}")
        return []


def get_feedback_history() -> Dict[str, Any]:
    """Get user feedback history for improving recommendations."""
    print("🧠 Analyzing feedback history...")

    try:
        def _get_feedback_data():
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            videos_worksheet = sheet.worksheet('videos')
            return videos_worksheet.get_all_records()

        videos_data = retry_on_quota_exceeded(_get_feedback_data)

        feedback_history = {
            'liked_channels': [],
            'disliked_channels': [],
            'liked_keywords': [],
            'disliked_keywords': [],
            'total_feedback': 0
        }

        for video in videos_data:
            rating = video.get('rating', '')
            channel = video.get('channel', '')
            title = video.get('video_title', '')

            if rating and channel:
                feedback_history['total_feedback'] += 1

                if rating in ['liked', 'loved']:
                    if channel not in feedback_history['liked_channels']:
                        feedback_history['liked_channels'].append(channel)

                    # Extract keywords from liked video titles
                    title_words = title.lower().split()
                    feedback_history['liked_keywords'].extend([w for w in title_words if len(w) > 4])

                elif rating in ['didn\'t_like', 'boring']:
                    if channel not in feedback_history['disliked_channels']:
                        feedback_history['disliked_channels'].append(channel)

                    # Extract keywords from disliked video titles
                    title_words = title.lower().split()
                    feedback_history['disliked_keywords'].extend([w for w in title_words if len(w) > 4])

        # Remove duplicates and limit size
        feedback_history['liked_keywords'] = list(set(feedback_history['liked_keywords']))[:20]
        feedback_history['disliked_keywords'] = list(set(feedback_history['disliked_keywords']))[:20]

        print(f"✅ Analyzed {feedback_history['total_feedback']} pieces of feedback")
        return feedback_history

    except Exception as e:
        print(f"❌ Error analyzing feedback history: {e}")
        return {'liked_channels': [], 'disliked_channels': [], 'liked_keywords': [], 'disliked_keywords': [], 'total_feedback': 0}


def record_video_recommendation(video_title: str, channel: str, topic: str, parent_topic: str, video_id: str, topic_row: int):
    """Record a video recommendation in Google Sheets."""
    print("📝 Recording video recommendation...")

    try:
        def _record_video():
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            videos_worksheet = sheet.worksheet('videos')

            today = get_current_date()
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # Append new row with video info
            videos_worksheet.append_row([
                video_title,
                channel,
                video_url,
                topic,
                parent_topic,
                today,  # date_recommended
                '',     # date_watched (empty initially)
                '',     # rating (empty initially)
                ''      # notes (empty initially)
            ])

        retry_on_quota_exceeded(_record_video)

        print("✅ Recorded video recommendation in Google Sheets")

    except Exception as e:
        print(f"❌ Error writing to Google Sheets: {e}")
        print("⚠️  Video recommendation not recorded, but continuing...")


def update_video_feedback(video_url: str, feedback: str):
    """Update video feedback in Google Sheets."""
    print(f"📝 Recording feedback: {feedback}")

    try:
        def _update_feedback():
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            videos_worksheet = sheet.worksheet('videos')

            # Get all records to find the right row
            all_records = videos_worksheet.get_all_values()
            today = get_current_date()

            for i, row in enumerate(all_records[1:], start=2):  # Skip header, start at row 2
                if len(row) >= 3 and row[2] == video_url:  # video_url is column C (index 2)
                    # Update rating (column H) and date_watched (column G)
                    videos_worksheet.update(f'G{i}', today)  # date_watched
                    videos_worksheet.update(f'H{i}', feedback)  # rating
                    print(f"✅ Updated feedback for video at row {i}")
                    return True

            print(f"❌ Video URL not found in sheets: {video_url}")
            return False

        return retry_on_quota_exceeded(_update_feedback)

    except Exception as e:
        print(f"❌ Error updating video feedback: {e}")
        return False


def update_video_notes(video_url: str, notes: str):
    """Update video notes in Google Sheets."""
    print(f"📝 Recording notes: {notes[:50]}...")

    try:
        def _update_notes():
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            videos_worksheet = sheet.worksheet('videos')

            # Get all records to find the right row
            all_records = videos_worksheet.get_all_values()

            for i, row in enumerate(all_records[1:], start=2):  # Skip header, start at row 2
                if len(row) >= 3 and row[2] == video_url:  # video_url is column C (index 2)
                    # Update notes (column I)
                    videos_worksheet.update(f'I{i}', notes)
                    print(f"✅ Updated notes for video at row {i}")
                    return True

            print(f"❌ Video URL not found in sheets: {video_url}")
            return False

        return retry_on_quota_exceeded(_update_notes)

    except Exception as e:
        print(f"❌ Error updating video notes: {e}")
        return False