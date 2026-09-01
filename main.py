#!/usr/bin/env python3
import json
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime

import discord
from dotenv import load_dotenv

# Import from our modular services
from src.utils import validate_environment
from src.youtube_service import search_youtube, filter_available_videos
from src.claude_service import get_claude_recommendation, analyze_topic_interest, generate_topic_expansion
from src.sheets_service import (
    get_google_sheets_client,
    get_next_topic,
    get_watched_videos,
    get_feedback_history,
    record_video_recommendation,
    update_video_feedback,
    update_video_notes
)
from src.discord_service import (
    create_video_embed,
    extract_video_info_from_embed,
    detect_video_request_pattern,
    add_feedback_reactions,
    get_feedback_from_reaction,
    extract_notes_from_reply
)
from src.bot import HobbyMaxxingBot

# Import environment variables and constants from utils
from src.utils import (
    YOUTUBE_API_KEY,
    ANTHROPIC_API_KEY,
    DISCORD_BOT_TOKEN,
    DISCORD_CHANNEL_ID,
    DISCORD_USER_ID,
    GOOGLE_SHEETS_ID,
    DATE_FORMAT,
    FEEDBACK_EMOJIS
)

# Constants now imported from utils

# validate_environment function now available from src.utils

# get_google_sheets_client now available from src.sheets_service

def calculate_topic_interest_scores() -> Dict[str, float]:
    """Calculate interest scores for topics based on recent ratings."""
    print("🧠 Calculating topic interest scores...")

    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)
        videos_worksheet = sheet.worksheet('videos')

        # Get all video records
        records = videos_worksheet.get_all_records()

        topic_scores = {}

        for record in records:
            topic = record.get('topic', '').lower()
            rating = record.get('rating', '')
            date_recommended = record.get('date_recommended', '')

            if not topic or not rating:
                continue

            # Convert rating to numeric score
            rating_scores = {
                'loved': 2.0,
                'liked': 1.0,
                'didn\'t_like': -0.5,
                'boring': -1.0
            }

            score = rating_scores.get(rating, 0)

            # Boost recent activity (within last 30 days)
            try:
                if date_recommended:
                    from datetime import datetime, timedelta
                    rec_date = datetime.strptime(date_recommended, DATE_FORMAT)
                    days_ago = (datetime.now() - rec_date).days

                    if days_ago <= 30:
                        recency_boost = max(0.5, 1.0 - (days_ago / 30))  # Linear decay over 30 days
                        score *= (1 + recency_boost)
            except:
                pass  # Skip date parsing errors

            if topic in topic_scores:
                topic_scores[topic] += score
            else:
                topic_scores[topic] = score

        print(f"✅ Calculated interest scores for {len(topic_scores)} topics")
        return topic_scores

    except Exception as e:
        print(f"❌ Error calculating topic scores: {e}")
        return {}

def get_next_topic() -> Tuple[str, str, str]:
    """Smart topic selection: prioritize unwatched topics and recent interests."""
    print("📊 Smart topic selection from Google Sheets...")

    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)
        topics_worksheet = sheet.worksheet('topics')

        # Get all records from the topics sheet
        records = topics_worksheet.get_all_records()

        if not records:
            print("❌ No topics found in the sheet - returning default topic")
            return "general learning", "", 2

        # Get interest scores from video ratings
        interest_scores = calculate_topic_interest_scores()

        # Create weighted candidates
        candidates = []

        for i, record in enumerate(records):
            topic = record['topic']
            parent_topic = record.get('parent_topic', '')
            date_watched = record.get('date_watched', '')

            # Base weight
            weight = 1.0

            # MASSIVE boost for never-watched topics (exploration priority)
            if not date_watched:
                weight *= 15.0  # 15x more likely to select unwatched topics
                print(f"🆕 Unwatched topic boost: {topic}")
            else:
                # Strong penalty for recently watched topics
                try:
                    from datetime import datetime, timedelta
                    watched_date = datetime.strptime(date_watched, DATE_FORMAT)
                    days_since_watched = (datetime.now() - watched_date).days

                    if days_since_watched < 3:
                        weight *= 0.05  # Very unlikely to reselect within 3 days
                        print(f"🚫 Strong recent penalty: {topic} ({days_since_watched} days ago)")
                    elif days_since_watched < 14:
                        weight *= 0.3  # Strong penalty for 2 weeks
                        print(f"🕒 Recent watch penalty: {topic} ({days_since_watched} days ago)")
                    elif days_since_watched < 30:
                        weight *= 0.6  # Moderate penalty for a month
                except:
                    pass  # Skip date parsing errors

            # Apply REDUCED interest score boost (less influence on selection)
            topic_lower = topic.lower()
            if topic_lower in interest_scores:
                interest_score = interest_scores[topic_lower]
                # Cap the interest boost to prevent domination
                capped_score = min(interest_score, 2.0) if interest_score > 0 else interest_score

                if capped_score > 0:
                    # Smaller multiplier for interest boost
                    weight *= (1 + capped_score * 0.3)  # Max 60% boost instead of 200%+
                    print(f"❤️ Interest boost for {topic}: {capped_score:.2f} (reduced)")
                elif capped_score < 0:
                    weight *= max(0.2, 1 + capped_score * 0.3)  # Gentler penalties too
                    print(f"👎 Interest penalty for {topic}: {capped_score:.2f}")

            # Add small random variation to prevent deterministic patterns
            import random
            weight *= random.uniform(0.8, 1.2)  # ±20% random variance

            candidates.append({
                'topic': topic,
                'parent_topic': parent_topic,
                'row': str(i + 2),  # +2 for 1-based index + header row
                'weight': weight
            })

        # Weighted random selection
        import random
        total_weight = sum(c['weight'] for c in candidates)

        if total_weight == 0:
            print("⚠️ All topics have zero weight, selecting randomly")
            selected = random.choice(candidates)
        else:
            # Pick random number and find corresponding candidate
            rand_val = random.uniform(0, total_weight)
            cumulative = 0
            selected = candidates[0]  # fallback

            for candidate in candidates:
                cumulative += candidate['weight']
                if rand_val <= cumulative:
                    selected = candidate
                    break

        topic = selected['topic']
        parent_topic = selected['parent_topic']
        row = selected['row']

        print(f"🎯 Smart selection: '{topic}' (parent: {parent_topic}) [weight: {selected['weight']:.2f}]")
        print(f"📊 Selection from {len(candidates)} candidates (total weight: {total_weight:.2f})")

        return topic, parent_topic, row

    except Exception as e:
        print(f"❌ Error in smart topic selection: {e}")
        print("🔄 Falling back to default topic...")
        return "general learning", "", 2

def get_watched_videos() -> Dict[str, bool]:
    """Get a dict of video URLs that have been watched or are still pending."""
    print("📖 Reading existing videos from Google Sheets...")

    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)
        videos_worksheet = sheet.worksheet('videos')

        # Get all records from the videos sheet
        records = videos_worksheet.get_all_records()

        watched_videos = {}
        for record in records:
            video_url = record.get('video_url', '')
            date_watched = record.get('date_watched', '')

            # Mark as unavailable if already watched (has date_watched)
            if video_url:
                watched_videos[video_url] = bool(date_watched)

        print(f"✅ Found {len(watched_videos)} videos in history ({sum(watched_videos.values())} watched)")
        return watched_videos

    except Exception as e:
        print(f"❌ Error reading videos from Google Sheets: {e}")
        return {}

def filter_available_videos(videos: List[Dict[str, Any]], watched_videos: Dict[str, bool]) -> List[Dict[str, Any]]:
    """Filter out videos that have already been watched."""
    available_videos = []

    for video in videos:
        video_url = f"https://www.youtube.com/watch?v={video['video_id']}"

        # Skip if this video has already been watched
        if video_url in watched_videos and watched_videos[video_url]:
            print(f"⏭️  Skipping already watched video: {video['title']}")
            continue

        # Skip if this video is pending (recommended but not watched yet)
        if video_url in watched_videos and not watched_videos[video_url]:
            print(f"⏭️  Skipping pending video: {video['title']}")
            continue

        available_videos.append(video)

    print(f"✅ {len(available_videos)} new videos available (filtered from {len(videos)} total)")
    return available_videos

def get_feedback_history() -> Dict[str, Any]:
    """Get user's feedback history to improve recommendations."""
    print("🧠 Analyzing feedback history...")

    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)
        videos_worksheet = sheet.worksheet('videos')

        # Get all records from the videos sheet
        records = videos_worksheet.get_all_records()

        feedback_data = {
            'loved_channels': [],
            'disliked_channels': [],
            'loved_keywords': [],
            'boring_keywords': [],
            'total_feedback': 0
        }

        for record in records:
            rating = record.get('rating', '')
            if not rating:
                continue

            feedback_data['total_feedback'] += 1
            video_title = record.get('video_title', '').lower()
            channel = record.get('channel', '')  # Updated to use 'channel' column

            if rating in ['loved', 'liked']:
                if channel:
                    feedback_data['loved_channels'].append(channel)
                # Extract keywords from titles of loved videos
                title_words = [word for word in video_title.split() if len(word) > 3]
                feedback_data['loved_keywords'].extend(title_words[:3])  # Top 3 words

            elif rating in ['didn\'t_like', 'boring']:
                if channel:
                    feedback_data['disliked_channels'].append(channel)
                # Extract keywords from boring/disliked videos to avoid
                title_words = [word for word in video_title.split() if len(word) > 3]
                feedback_data['boring_keywords'].extend(title_words[:3])

        # Count occurrences and get most common
        from collections import Counter
        feedback_data['loved_channels'] = [item[0] for item in Counter(feedback_data['loved_channels']).most_common(3)]
        feedback_data['disliked_channels'] = [item[0] for item in Counter(feedback_data['disliked_channels']).most_common(3)]
        feedback_data['loved_keywords'] = [item[0] for item in Counter(feedback_data['loved_keywords']).most_common(5)]
        feedback_data['boring_keywords'] = [item[0] for item in Counter(feedback_data['boring_keywords']).most_common(5)]

        print(f"✅ Analyzed {feedback_data['total_feedback']} pieces of feedback")
        return feedback_data

    except Exception as e:
        print(f"❌ Error reading feedback history: {e}")
        return {'loved_channels': [], 'disliked_channels': [], 'loved_keywords': [], 'boring_keywords': [], 'total_feedback': 0}

def update_video_feedback(video_url: str, feedback: str):
    """Update the rating for a specific video in Google Sheets."""
    print(f"📝 Recording rating: {feedback} for video")

    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)
        videos_worksheet = sheet.worksheet('videos')

        # Get all records to find the right row
        records = videos_worksheet.get_all_records()

        topic_to_update = None
        for i, record in enumerate(records):
            if record.get('video_url') == video_url:
                row_num = i + 2  # +2 for 1-based index + header row
                topic_to_update = record.get('topic', '')

                # Update rating column (column 8 in new structure)
                # video_title | channel | video_url | topic | parent_topic | date_recommended | date_watched | rating | notes
                videos_worksheet.update_cell(row_num, 8, feedback)

                # If positive feedback, also update date_watched
                if feedback in ['liked', 'loved']:
                    today = datetime.now().strftime(DATE_FORMAT)
                    videos_worksheet.update_cell(row_num, 7, today)  # date_watched is column 7
                    print(f"✅ Updated rating: {feedback} + marked as watched ({today})")

                    # Update topics sheet with date_watched when positive feedback
                    if topic_to_update:
                        update_topic_last_watched(topic_to_update, today)
                else:
                    print(f"✅ Updated rating: {feedback} (not marked as watched)")

                return

        print("❌ Video not found in sheet")

    except Exception as e:
        print(f"❌ Error updating rating: {e}")

def update_topic_last_watched(topic: str, date_watched: str):
    """Update the date_watched for a topic in the topics sheet."""
    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)
        topics_worksheet = sheet.worksheet('topics')

        # Get all records to find the right topic row
        records = topics_worksheet.get_all_records()

        for i, record in enumerate(records):
            if record.get('topic', '').lower() == topic.lower():
                row_num = i + 2  # +2 for 1-based index + header row

                # Update date_watched column (assuming it's the 4th column based on your description)
                # topic | parent_topic | date_added | date_watched | video_title
                topics_worksheet.update_cell(row_num, 4, date_watched)
                print(f"✅ Updated topic '{topic}' date_watched to {date_watched}")
                return

        print(f"⚠️  Topic '{topic}' not found in topics sheet")

    except Exception as e:
        print(f"❌ Error updating topic date_watched: {e}")

def record_video_recommendation(video_title: str, channel: str, topic: str, parent_topic: str, video_id: str, topic_row: str):
    """Record the recommended video in the 'videos' sheet and update the 'topics' sheet."""
    print("📝 Recording video recommendation...")

    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID)

        # Add to 'videos' sheet
        videos_worksheet = sheet.worksheet('videos')
        today = datetime.now().strftime(DATE_FORMAT)
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Append new row to videos sheet with updated column structure:
        # video_title | channel | video_url | topic | parent_topic | date_recommended | date_watched | rating | notes
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

        # Update 'topics' sheet to mark this topic with the video title
        topics_worksheet = sheet.worksheet('topics')

        print("✅ Recorded video recommendation in Google Sheets")

    except Exception as e:
        print(f"❌ Error writing to Google Sheets: {e}")
        print("⚠️  Continuing without recording to sheets...")

def search_youtube(topic: str, parent_topic: str = "", max_results: int = 8) -> List[Dict[str, Any]]:
    """Search YouTube for videos on the given topic."""
    # Enhance search query with parent topic for better targeting
    search_query = topic

    if parent_topic and parent_topic.lower() not in topic.lower():
        # Add parent topic to make search more specific
        search_query = f"{topic} {parent_topic}"

    print(f"🔍 Searching YouTube for: '{search_query}'...")

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # Search for videos
        search_response = youtube.search().list(
            q=search_query,
            part="snippet",
            maxResults=max_results,
            type="video",
            order="relevance"
        ).execute()

        videos = []
        for item in search_response["items"]:
            video_data = {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"][:500],  # Truncate long descriptions
                "channel_title": item["snippet"]["channelTitle"],
                "thumbnail_url": item["snippet"]["thumbnails"]["medium"]["url"]
            }
            videos.append(video_data)

        print(f"✅ Found {len(videos)} video results")
        return videos

    except Exception as e:
        print(f"❌ Error searching YouTube: {e}")
        print("🔄 Returning empty video list...")
        return []

def get_claude_recommendation(videos: List[Dict[str, Any]], topic: str, feedback_history: Dict[str, Any]) -> Dict[str, str]:
    """Ask Claude to pick the best video and write a blurb."""
    print("🤖 Asking Claude to pick the best video...")

    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Format video candidates for Claude
        candidates_text = "\n\n".join([
            f"Video {i+1}:\n"
            f"Title: {video['title']}\n"
            f"Channel: {video['channel_title']}\n"
            f"Description: {video['description']}\n"
            f"Video ID: {video['video_id']}"
            for i, video in enumerate(videos)
        ])

        # Build feedback context for Claude
        feedback_context = ""
        if feedback_history['total_feedback'] > 0:
            feedback_context = f"""

User's preferences based on past feedback:
- Loved channels: {', '.join(feedback_history['loved_channels']) if feedback_history['loved_channels'] else 'None yet'}
- Disliked channels: {', '.join(feedback_history['disliked_channels']) if feedback_history['disliked_channels'] else 'None yet'}
- Prefers content with: {', '.join(feedback_history['loved_keywords']) if feedback_history['loved_keywords'] else 'No pattern yet'}
- Finds boring: {', '.join(feedback_history['boring_keywords']) if feedback_history['boring_keywords'] else 'None yet'}

Please heavily prioritize channels and content styles the user has loved, and avoid channels and keywords they've found boring."""

        prompt = f"""You are helping someone discover the best YouTube video to learn about "{topic}".

Here are the candidate videos:

{candidates_text}{feedback_context}

Please pick the single best video for someone just starting to learn about {topic}. Consider factors like:
- Educational value and clarity
- Channel reputation
- Content quality indicators in title/description
- Beginner-friendliness
- User's past feedback and preferences

Return your answer as valid JSON with exactly these fields:
- "video_id": the ID of the chosen video
- "blurb": a 1-2 sentence encouraging the viewer to watch the video to further their {topic} in a casual yet excited tone of voice with use of
  language typical of people who enjoy {topic} if the slang fits. Emphasize how the video can get them where they want to be in an aspirational and motivational way.
  Avoid generic phrases like "this video is great" or "you should watch this". Instead, focus on the unique value of the video and how it can help the viewer achieve their goals in {topic}.

Your response must be valid JSON only, no other text."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Claude Haiku 4.5
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse Claude's JSON response
        response_text = response.content[0].text.strip()

        # Extract JSON from markdown code blocks if present
        if response_text.startswith('```json'):
            # Find the JSON content between ```json and ```
            start = response_text.find('```json') + 7
            end = response_text.rfind('```')
            json_text = response_text[start:end].strip()
        elif response_text.startswith('```'):
            # Handle plain ``` code blocks
            start = response_text.find('```') + 3
            end = response_text.rfind('```')
            json_text = response_text[start:end].strip()
        else:
            # No code blocks, use the response as-is
            json_text = response_text

        recommendation = json.loads(json_text)

        print(f"✅ Claude picked video ID: {recommendation['video_id']}")
        return recommendation

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing Claude's response as JSON: {e}")
        print(f"Full response was: {response.content[0].text}")
        print(f"Extracted JSON text was: {json_text}")
        # Return fallback recommendation instead of crashing
        return {
            "video_id": videos[0]["video_id"] if videos else "unknown",
            "blurb": f"A great video to help you learn more about {topic}!"
        }
    except Exception as e:
        print(f"❌ Error getting Claude recommendation: {e}")
        # Return fallback recommendation instead of crashing
        return {
            "video_id": videos[0]["video_id"] if videos else "unknown",
            "blurb": f"An interesting video about {topic} to check out!"
        }

class HobbyMaxxingBot:
    """Persistent Discord bot that handles video recommendations and feedback."""

    def __init__(self):
        # Initialize Discord client with minimal intents
        intents = discord.Intents.default()
        intents.message_content = True  # Need this to read follow-up responses
        intents.guild_reactions = True  # Need this to listen for reactions

        self.client = discord.Client(intents=intents)

        # Track videos waiting for notes
        self.awaiting_notes = {}  # message_id -> {video_url, topic, asked_at}

        # Track posted videos for context
        self.posted_videos = {}  # message_id -> {video_url, topic, video_title}

        # Track topic expansion requests
        self.awaiting_topic_selection = {}  # message_id -> {original_topic, parent_topic, suggested_topics}

        # Track organic topic exploration conversations
        self.exploring_topic_interest = {}  # message_id -> {raw_topic, analysis, step, existing_topics}

        # Graceful shutdown system
        self.should_shutdown = False  # Flag to initiate shutdown
        self.workflow_complete = False  # Flag indicating workflow completion
        self.shutdown_timeout_hours = 24  # Timeout before auto-shutdown (hours)

        self.setup_events()

    def setup_events(self):
        """Set up Discord event handlers."""

        @self.client.event
        async def on_ready():
            print(f"🤖 Connected as {self.client.user}")
            print("✅ Bot is ready to receive feedback and notes!")

        @self.client.event
        async def on_message(message):
            """Handle follow-up messages for notes collection."""
            print(f"🔍 Message received from {message.author.display_name}: {message.content[:50]}...")

            # Don't respond to our own messages
            if message.author == self.client.user:
                print("⏭️  Ignoring own message")
                return

            # Only process messages from the specified user
            if message.author.id != DISCORD_USER_ID:
                print(f"⏭️  Ignoring message from user {message.author.id} (expected {DISCORD_USER_ID})")
                return

            print(f"✅ Valid user message detected. Checking awaiting_notes...")
            print(f"📋 Currently awaiting notes for {len(self.awaiting_notes)} videos")
            print(f"📋 Currently awaiting topic selections for {len(self.awaiting_topic_selection)} requests")
            print(f"📋 Currently exploring topic interests for {len(self.exploring_topic_interest)} conversations")

            # Check if this is a response to a topic selection request
            channel_id = message.channel.id
            found_match = False

            # First, check for topic interest exploration responses
            for msg_id, data in list(self.exploring_topic_interest.items()):
                if data['channel_id'] == channel_id:
                    found_match = True
                    print(f"🔍 TOPIC EXPLORATION RESPONSE! Processing: {message.content[:50]}...")

                    # Process topic exploration response
                    success = await self.process_topic_exploration_response(message.content, data, message)

                    if success:
                        # Remove from awaiting list
                        del self.exploring_topic_interest[msg_id]
                    break

            # If not topic exploration, check for topic selection responses
            if not found_match:
                for msg_id, data in list(self.awaiting_topic_selection.items()):
                    if data['channel_id'] == channel_id:
                        found_match = True
                        print(f"🎯 TOPIC SELECTION RESPONSE! Processing: {message.content[:50]}...")

                        # Process topic selection
                        success = await self.process_topic_selection(message.content, data, message)

                        if success:
                            # Remove from awaiting list
                            del self.awaiting_topic_selection[msg_id]
                        break

            # If not topic selection, check for notes request
            if not found_match:
                for msg_id, data in list(self.awaiting_notes.items()):
                    print(f"🔍 Checking awaiting note: channel {data['channel_id']} vs current {channel_id}")
                    if data['channel_id'] == channel_id:
                        found_match = True
                        # User responded! Capture their notes
                        video_url = data['video_url']
                        user_notes = message.content[:500]  # Limit to 500 chars

                        print(f"📝 NOTES MATCH FOUND! Recording notes: {user_notes[:50]}...")

                        # Update Google Sheets with the notes
                        self.update_video_notes(video_url, user_notes)

                        # Thank the user
                        await message.add_reaction("✅")
                        await message.reply("Thanks! Your reflection has been recorded. 🎯")

                        # Remove from awaiting list
                        del self.awaiting_notes[msg_id]
                        break

            if not found_match:
                # Check if this is an organic interest expression
                interest_detected = await self.detect_topic_interest(message.content, message.channel)

                if not interest_detected:
                    print(f"❌ No matching awaiting requests or interest detected for channel {channel_id}")
                    # For debugging: show all awaiting requests
                    for msg_id, data in self.awaiting_notes.items():
                        print(f"   - Waiting for notes on channel {data['channel_id']} for video {data['topic']}")
                    for msg_id, data in self.awaiting_topic_selection.items():
                        print(f"   - Waiting for topic selection on channel {data['channel_id']} for {data['original_topic']}")
                    for msg_id, data in self.exploring_topic_interest.items():
                        print(f"   - Exploring topic interest on channel {data['channel_id']} for {data['raw_topic']}")

                    # Test command for debugging
                    if message.content.lower() == "test":
                        await message.reply("✅ Bot is receiving messages correctly!")

                    # Check for manual video requests (natural language patterns)
                    if await self.is_video_request(message.content):
                        await self.show_topic_menu(message)

        @self.client.event
        async def on_message_edit(message_before, message_after):
            """Handle message edits - treat as new message for notes."""
            await self.client.get_event('on_message')(message_after)

        @self.client.event
        async def on_reaction_add(reaction, user):
            """Handle reaction feedback from the user."""
            # Only process reactions from the specified user
            if user.id != DISCORD_USER_ID:
                return

            # Only process our feedback emojis
            emoji_str = str(reaction.emoji)
            if emoji_str not in FEEDBACK_EMOJIS:
                return

            # Get the message that was reacted to
            message = reaction.message

            # Check if this is one of our bot messages with a video embed
            if not message.embeds or not message.author.bot:
                return

            embed = message.embeds[0]
            video_url = embed.url

            # Get video info from stored data or extract from embed
            video_info = self.posted_videos.get(message.id)
            if video_info:
                topic = video_info['topic']
                video_title = video_info['video_title']
            else:
                # Extract info from Discord embed (for cross-process compatibility)
                video_title = embed.title
                footer_text = embed.footer.text if embed.footer else ""
                topic = ""

                # Parse topic from footer: "Channel: X • Topic: Y"
                if "Topic:" in footer_text:
                    topic = footer_text.split("Topic:")[-1].strip()

                if not topic or not video_title:
                    print("❌ Could not extract video info from embed")
                    print(f"   Title: {video_title}")
                    print(f"   Footer: {footer_text}")
                    return

                print(f"📖 Extracted video info from embed: {topic}")

            print(f"🎯 Processing reaction for: {video_title} (Topic: {topic})")

            # Map emoji to feedback
            feedback = FEEDBACK_EMOJIS[emoji_str]

            print(f"📝 Received feedback: {feedback} ({emoji_str}) for video: {embed.title}")

            # Update Google Sheets with feedback
            update_video_feedback(video_url, feedback)

            # Update the embed to show feedback was received
            embed.color = 0x00FF00  # Green for feedback received

            # Show different messages based on feedback type
            if feedback in ['liked', 'loved']:
                status_msg = f"{emoji_str} {feedback.replace('_', ' ').title()} - Marked as watched!"
            else:
                status_msg = f"{emoji_str} {feedback.replace('_', ' ').title()} - Skipped"

            embed.add_field(
                name="Rating Received",
                value=status_msg,
                inline=False
            )

            await message.edit(embed=embed)
            print("✅ Rating recorded and message updated!")

            # Ask for learning notes regardless of rating
            await self.ask_for_notes(message.channel, video_url, topic, video_title)

    def update_video_notes(self, video_url: str, notes: str):
        """Update the notes for a specific video in Google Sheets."""
        print(f"📝 Recording notes: {notes[:50]}...")

        try:
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            videos_worksheet = sheet.worksheet('videos')

            # Get all records to find the right row
            records = videos_worksheet.get_all_records()

            for i, record in enumerate(records):
                if record.get('video_url') == video_url:
                    row_num = i + 2  # +2 for 1-based index + header row

                    # Update notes column (column 9 in new structure)
                    # video_title | channel | video_url | topic | parent_topic | date_recommended | date_watched | rating | notes
                    videos_worksheet.update_cell(row_num, 9, notes)
                    print(f"✅ Updated notes for video")

                    # Set workflow completion flags for graceful shutdown
                    self.workflow_complete = True
                    self.should_shutdown = True
                    print("🏁 Workflow complete - notes recorded. Bot will shut down gracefully.")
                    return

            print("❌ Video not found in sheet for notes update")

        except Exception as e:
            print(f"❌ Error updating notes: {e}")

    async def ask_for_notes(self, channel, video_url: str, topic: str, video_title: str):
        """Ask the user for their learning notes/reflections."""
        try:
            # Generate a thoughtful question based on the topic
            question = self.generate_reflection_question(topic, video_title)

            print(f"🤔 Asking follow-up question: {question}")

            # Post the follow-up question
            follow_up_msg = await channel.send(f"🤔 {question}")

            # Track this request
            self.awaiting_notes[follow_up_msg.id] = {
                'video_url': video_url,
                'topic': topic,
                'channel_id': channel.id,
                'asked_at': datetime.now()
            }

            print(f"✅ Asked for reflection notes on channel {channel.id}")
            print(f"📋 Now awaiting notes for {len(self.awaiting_notes)} videos")

        except Exception as e:
            print(f"❌ Error asking for notes: {e}")

    def generate_reflection_question(self, topic: str, video_title: str) -> str:
        """Generate a universal reflection question that works for any topic."""
        import random

        # Universal reflection questions that work for any learning topic
        universal_questions = [
            f"How does this change your understanding of {topic}?",
            f"What's one thing from '{video_title}' that you'll remember?",
            f"What are your thoughts on the video?",
            f"What was your biggest takeaway from '{video_title}'?",
            f"What surprised you most about this {topic} video?",
            f"How will this video influence your approach to {topic}?",
            f"What's one insight from '{video_title}' that stuck with you?",
            f"What questions did this video raise for you about {topic}?",
            f"What would you like to explore more after watching '{video_title}'?",
            f"How did this video expand your perspective on {topic}?",
            f"What's something from '{video_title}' you want to try or apply?",
            f"What resonated with you most in this video?"
        ]

        return random.choice(universal_questions)

    def generate_related_topics(self, original_topic: str, parent_topic: str = '') -> List[str]:
        """Use Claude to generate related topic suggestions."""
        print(f"🧠 Generating related topics for: {original_topic}")

        try:
            # Use the robust topic expansion function from claude_service
            return generate_topic_expansion(original_topic, parent_topic)

        except Exception as e:
            print(f"❌ Error generating related topics: {e}")
            # Fallback generic suggestions based on original topic
            return [
                f"advanced {original_topic}",
                f"beginner {original_topic}",
                f"{original_topic} techniques",
                f"{original_topic} equipment",
                f"{original_topic} tips"
            ]

    async def ask_for_topic_expansion(self, channel, original_topic: str, parent_topic: str = ''):
        """Ask user to select new related topics to explore."""
        try:
            # Generate related topic suggestions
            suggested_topics = self.generate_related_topics(original_topic, parent_topic)

            if not suggested_topics:
                print("❌ No topic suggestions generated")
                return

            # Format the message
            topics_list = "\n".join([f"**{i+1}.** {topic}" for i, topic in enumerate(suggested_topics)])

            message_text = f"""🤔 **No more new videos found for '{original_topic}'!**

Here are some related topics you could explore next:

{topics_list}

**How to respond:**
• Type the **numbers** of topics you want (e.g., "1 3 5")
• Or type **topic names** directly (e.g., "advanced guitar techniques")
• You can select **multiple topics** - I'll add them all!

What interests you? 🎯"""

            # Send the message
            expansion_msg = await channel.send(message_text)

            # Track this request
            self.awaiting_topic_selection[expansion_msg.id] = {
                'original_topic': original_topic,
                'parent_topic': parent_topic,
                'suggested_topics': suggested_topics,
                'channel_id': channel.id,
                'asked_at': datetime.now()
            }

            print(f"✅ Asked for topic expansion with {len(suggested_topics)} suggestions")

        except Exception as e:
            print(f"❌ Error asking for topic expansion: {e}")

    async def process_topic_selection(self, user_response: str, selection_data: dict, message) -> bool:
        """Process user's topic selection and add to Google Sheets."""
        try:
            # Check if this is a video request menu selection
            if selection_data.get('type') == 'video_request_menu':
                return await self.handle_video_topic_selection(user_response, selection_data, message)

            # Original topic expansion logic
            suggested_topics = selection_data['suggested_topics']
            original_topic = selection_data['original_topic']
            parent_topic = selection_data['parent_topic']

            selected_topics = []

            # Parse user response - could be numbers or topic names
            user_input = user_response.lower().strip()

            # Check for numbers first (1 3 5)
            numbers = [int(x) for x in user_input.split() if x.isdigit()]
            for num in numbers:
                if 1 <= num <= len(suggested_topics):
                    topic = suggested_topics[num - 1]
                    if topic not in selected_topics:
                        selected_topics.append(topic)

            # If no numbers found, treat as topic names
            if not selected_topics:
                # First try exact matches with suggested topics
                for suggested in suggested_topics:
                    if user_input == suggested.lower():
                        selected_topics.append(suggested)
                        break

                # If no exact match found, treat as custom topic
                if not selected_topics and len(user_input) > 3:
                    selected_topics.append(user_response.strip())

            if not selected_topics:
                await message.reply("❌ I couldn't understand your selection. Please try again with numbers (e.g. '1 3') or topic names.")
                return False

            print(f"📝 Selected topics: {selected_topics}")

            # Add topics to Google Sheets
            success = self.add_topics_to_sheet(selected_topics, parent_topic or original_topic)

            if success:
                topics_text = "\n".join([f"• {topic}" for topic in selected_topics])
                await message.add_reaction("✅")
                await message.reply(f"🎯 **Added {len(selected_topics)} new topics:**\n{topics_text}\n\nLet me find a video from one of these topics!")

                # Continue with video recommendation from new topics
                await self.continue_with_new_topics(message.channel, selected_topics)
                return True
            else:
                await message.reply("❌ Sorry, there was an error adding the topics. Please try again.")
                return False

        except Exception as e:
            print(f"❌ Error processing topic selection: {e}")
            await message.reply("❌ There was an error processing your selection. Please try again.")
            return False

    def add_topics_to_sheet(self, topics: List[str], parent_topic: str = '') -> bool:
        """Add new topics to the Google Sheets topics worksheet."""
        try:
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            topics_worksheet = sheet.worksheet('topics')

            today = datetime.now().strftime(DATE_FORMAT)

            # Add each topic as a new row
            for topic in topics:
                # topic | parent_topic | date_added | date_watched | video_title
                topics_worksheet.append_row([
                    topic,
                    parent_topic,
                    today,  # date_added
                    '',     # date_watched (empty)
                    ''      # video_title (empty)
                ])

            print(f"✅ Added {len(topics)} topics to sheet")
            return True

        except Exception as e:
            print(f"❌ Error adding topics to sheet: {e}")
            return False

    async def continue_with_new_topics(self, channel, new_topics: List[str]):
        """Continue the main flow with newly added topics."""
        try:
            print(f"🎯 Continuing with {len(new_topics)} new topics...")

            # Pick the first new topic and search for videos
            topic = new_topics[0]
            print(f"📌 Using first new topic: {topic}")

            # Get feedback history for personalized recommendations
            feedback_history = get_feedback_history()

            # Search YouTube for this topic (no parent topic for new topics)
            all_videos = search_youtube(topic)

            # No need to filter - these are guaranteed to be new videos
            available_videos = all_videos

            if not available_videos:
                await channel.send(f"❌ Couldn't find any videos for '{topic}' either. Let me try another topic...")
                if len(new_topics) > 1:
                    await self.continue_with_new_topics(channel, new_topics[1:])
                else:
                    await channel.send("😅 Having trouble finding videos for the new topics. Please try again later or add different topics.")
                return

            # Get Claude's recommendation
            recommendation = get_claude_recommendation(available_videos, topic, feedback_history)

            # Find the selected video
            selected_video = None
            for video in available_videos:
                if video["video_id"] == recommendation["video_id"]:
                    selected_video = video
                    break

            if not selected_video:
                print(f"❌ Could not find video with ID {recommendation['video_id']}")
                return

            # Record in Google Sheets - need to find the row number for this topic
            # Since we just added it, it should be one of the last rows
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            topics_worksheet = sheet.worksheet('topics')
            records = topics_worksheet.get_all_records()

            topic_row = None
            for i, record in enumerate(records):
                if record['topic'].lower() == topic.lower():
                    topic_row = str(i + 2)  # +2 for 1-based index + header
                    break

            if topic_row:
                record_video_recommendation(
                    selected_video["title"],
                    selected_video["channel_title"],
                    topic,
                    '',  # parent_topic - could enhance this
                    recommendation["video_id"],
                    topic_row
                )

            # Post the video recommendation
            await self.post_video_recommendation(
                recommendation["video_id"],
                recommendation["blurb"],
                available_videos,
                topic
            )

        except Exception as e:
            print(f"❌ Error continuing with new topics: {e}")
            import traceback
            traceback.print_exc()
            await channel.send(f"❌ There was an error finding a video for the new topics: {e}")

    async def detect_topic_interest(self, message_content: str, channel) -> bool:
        """Detect if user is expressing interest in a topic organically."""
        try:
            content_lower = message_content.lower().strip()

            # Pattern matching for interest expressions
            interest_patterns = [
                r"i'm (?:kind of |really |getting )?interested in (.+)",
                r"i've been (?:really )?interested in (.+)",
                r"i have been (?:really )?interested in (.+)",
                r"i'm (?:getting |really )?into (.+)",
                r"i've been (?:getting )?into (.+)",
                r"i want to (?:learn|try|explore|get into) (.+)",
                r"i'd like to (?:learn|try|explore|get into) (.+)",
                r"i've been thinking about (.+)",
                r"i have been thinking about (.+)",
                r"i'm curious about (.+)",
                r"i'm (?:really )?curious about (.+)",
                r"what about (.+)",
                r"i'd love to learn (.+)",
                r"thinking of getting into (.+)",
                r"been thinking about (.+)",
                r"lately i've been interested in (.+)",
                r"recently i've been interested in (.+)",
                r"(?:lately|recently) i'm interested in (.+)",
            ]

            import re
            extracted_topic = None

            print(f"🔍 Checking message for interest patterns: '{content_lower}'")

            for i, pattern in enumerate(interest_patterns):
                match = re.search(pattern, content_lower)
                if match:
                    extracted_topic = match.group(1).strip()
                    print(f"✅ PATTERN MATCH #{i}: '{pattern}' → extracted: '{extracted_topic}'")
                    break
                else:
                    print(f"⏭️  Pattern #{i} no match: '{pattern}'")

            if not extracted_topic or len(extracted_topic) < 3:
                print(f"❌ No valid topic extracted (topic: '{extracted_topic}', length: {len(extracted_topic) if extracted_topic else 0})")
                return False

            print(f"🎯 ORGANIC INTEREST DETECTED! Topic: '{extracted_topic}'")

            # Get existing topics from Google Sheets for intersection analysis
            existing_topic_tuples = self.get_existing_topics()
            existing_topics = [topic for topic, _ in existing_topic_tuples]  # Extract just topic names

            # Start topic exploration flow
            await self.start_topic_exploration(channel, extracted_topic, existing_topics)
            return True

        except Exception as e:
            print(f"❌ Error detecting topic interest: {e}")
            return False

    def get_existing_topics(self) -> List[Tuple[str, str]]:
        """Get all existing topics from Google Sheets as (topic, parent_topic) tuples."""
        try:
            client = get_google_sheets_client()
            sheet = client.open_by_key(GOOGLE_SHEETS_ID)
            topics_worksheet = sheet.worksheet('topics')

            records = topics_worksheet.get_all_records()
            topics = []
            for record in records:
                topic = record.get('topic', '').strip()
                parent_topic = record.get('parent_topic', '').strip()
                if topic:
                    topics.append((topic, parent_topic))

            print(f"📊 Retrieved {len(topics)} existing topics for intersection analysis")
            return topics

        except Exception as e:
            print(f"❌ Error getting existing topics: {e}")
            return []

    async def start_topic_exploration(self, channel, raw_topic: str, existing_topics: List[str]):
        """Analyze the topic and start exploration conversation."""
        try:
            print(f"🧠 Starting topic exploration for: '{raw_topic}'")

            # Use Claude to analyze the topic
            analysis = await self.analyze_topic_interest(raw_topic, existing_topics)

            if not analysis:
                await channel.send(f"🤔 I noticed you mentioned '{raw_topic}' but I'm having trouble analyzing it. Could you be more specific?")
                return

            # Start conversation based on analysis
            if analysis.get('needs_clarification', False):
                await self.ask_for_topic_clarification(channel, raw_topic, analysis)
            else:
                await self.suggest_topic_expansion(channel, raw_topic, analysis)

        except Exception as e:
            print(f"❌ Error starting topic exploration: {e}")
            await channel.send(f"❌ There was an error exploring '{raw_topic}'. Please try again.")

    async def analyze_topic_interest(self, raw_topic: str, existing_topics: List[str]) -> Dict[str, Any]:
        """Use Claude to analyze the user's topic interest and suggest expansions."""
        try:
            existing_topics_text = "\n".join([f"- {topic}" for topic in existing_topics[:20]])  # Limit to avoid token overflow

            prompt = f"""The user expressed interest in: "{raw_topic}"

Their existing interests include:
{existing_topics_text or "- (no existing topics yet)"}

Analyze this interest and provide a JSON response with:
1. "is_specific": true/false - is the topic specific enough to find videos?
2. "needs_clarification": true/false - does it need more clarification?
3. "suggested_parent": string - what's the broader category this falls under?
4. "specific_subtopics": array - 4-6 specific subtopics within this area
5. "intersection_topics": array - 2-3 topics that combine this with their existing interests
6. "beginner_friendly": array - 2-3 beginner-friendly entry points

Example for "guitar":
{{
  "is_specific": false,
  "needs_clarification": true,
  "suggested_parent": "music",
  "specific_subtopics": ["acoustic guitar basics", "electric guitar techniques", "fingerpicking", "chord progressions", "guitar maintenance"],
  "intersection_topics": ["guitar for surf rock", "cooking while listening to guitar music"],
  "beginner_friendly": ["basic guitar chords", "guitar for absolute beginners", "choosing your first guitar"]
}}

Return only valid JSON, no other text."""

            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Extract JSON from markdown if present
            if response_text.startswith('```json'):
                start = response_text.find('```json') + 7
                end = response_text.rfind('```')
                json_text = response_text[start:end].strip()
            elif response_text.startswith('```'):
                start = response_text.find('```') + 3
                end = response_text.rfind('```')
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text

            analysis = json.loads(json_text)
            print(f"✅ Topic analysis complete: {analysis.get('suggested_parent', 'unknown')} domain")
            return analysis

        except Exception as e:
            print(f"❌ Error analyzing topic interest: {e}")
            return {}

    async def ask_for_topic_clarification(self, channel, raw_topic: str, analysis: Dict[str, Any]):
        """Ask user to clarify and confirm parent topic."""
        try:
            suggested_parent = analysis.get('suggested_parent', 'general hobby')
            subtopics = analysis.get('specific_subtopics', [])
            beginner_topics = analysis.get('beginner_friendly', [])

            # Combine all suggestions with numbers
            all_suggestions = subtopics[:6] + beginner_topics[:3]
            unique_suggestions = []
            seen = set()
            for topic in all_suggestions:
                if topic.lower() not in seen and len(unique_suggestions) < 8:
                    unique_suggestions.append(topic)
                    seen.add(topic.lower())

            numbered_suggestions = "\n".join([f"**{i+1}.** {topic}" for i, topic in enumerate(unique_suggestions)])

            message_text = f"""💭 **I see you're interested in '{raw_topic}'!**

I think this falls under **{suggested_parent}**. Here are some specific topics you could explore:

{numbered_suggestions}

**Please respond with:**
• **"yes"** + **your topic choices** (e.g., "yes, I want 1 3 5" or "yes, map awareness and positioning")
• **Different parent** + **topics** (e.g., "actually gaming, I want items 2 4 6")
• **Custom topics** (e.g., "yes, support role tips, tank positioning, hero guides")

What interests you? 🎯"""

            exploration_msg = await channel.send(message_text)

            # Track this conversation with the numbered suggestions
            self.exploring_topic_interest[exploration_msg.id] = {
                'raw_topic': raw_topic,
                'analysis': analysis,
                'step': 'parent_confirmation',
                'channel_id': channel.id,
                'existing_topics': self.get_existing_topics(),
                'suggested_topics': unique_suggestions,
                'asked_at': datetime.now()
            }

            print(f"✅ Asked for parent topic clarification")

        except Exception as e:
            print(f"❌ Error asking for topic clarification: {e}")

    async def is_video_request(self, message_content):
        """Check if message is a natural video request."""
        content_lower = message_content.lower().strip()

        # Direct keywords
        direct_keywords = ['video', 'recommend', 'show me videos', 'topics']
        if any(keyword in content_lower for keyword in direct_keywords):
            return True

        # Natural language patterns
        request_patterns = [
            # "Can you" patterns
            r'can you.*recommend.*me.*',
            r'can you.*send.*me.*video',
            r'can you.*show.*me.*',
            r'can you.*find.*me.*',
            r'can you.*pick.*something',

            # "I" statements
            r'i need.*something.*to.*watch',
            r'i want.*to.*watch.*',
            r'i\'m.*looking.*for.*',
            r'i.*need.*video',
            r'i.*want.*video',

            # Question patterns
            r'what.*should.*i.*watch',
            r'what.*can.*i.*learn',
            r'got.*any.*recommendations',
            r'any.*suggestions',

            # Simple requests
            r'send.*me.*something',
            r'show.*me.*something',
            r'give.*me.*something',
            r'pick.*something.*for.*me',
            r'something.*to.*watch',
            r'something.*to.*learn',

            # Casual requests
            r'what.*to.*watch',
            r'need.*entertainment',
            r'bored.*',
            r'looking.*for.*content',
        ]

        import re
        for pattern in request_patterns:
            if re.search(pattern, content_lower):
                return True

        return False

    async def show_topic_menu(self, message):
        """Show available topics menu for manual video requests."""
        try:
            # Get all existing topics
            existing_topics = self.get_existing_topics()

            if not existing_topics:
                await message.reply("❌ **No topics found!**\n\nAdd some topics first by saying something like:\n*\"I'm interested in guitar\"*")
                return

            # Create numbered list - show all topics
            topic_list = []
            for i, (topic, parent_topic) in enumerate(existing_topics):
                topic_list.append(f"**{i+1}.** {topic} *({parent_topic})*")

            # Add surprise option
            surprise_number = len(topic_list) + 1
            topic_list.append(f"**{surprise_number}.** 🎲 Surprise me!")

            topics_text = "\n".join(topic_list)

            menu_text = f"""🎯 **Pick a topic for a video recommendation:**

{topics_text}

**Reply with the number** (e.g., "3" or "surprise me")"""

            # Send the menu
            menu_message = await message.reply(menu_text)

            # Track this request
            self.awaiting_topic_selection[menu_message.id] = {
                'type': 'video_request_menu',
                'available_topics': existing_topics,
                'surprise_number': surprise_number,
                'original_message': message,
                'channel_id': message.channel.id,
                'asked_at': datetime.now()
            }

            print(f"✅ Showed video topic menu with {len(existing_topics)} topics")

        except Exception as e:
            print(f"❌ Error showing topic menu: {e}")
            await message.reply("❌ Sorry, couldn't load your topics right now. Try again later!")

    async def handle_video_topic_selection(self, user_response: str, selection_data: Dict, message) -> bool:
        """Handle video topic selection from menu."""
        try:
            response = user_response.strip()
            available_topics = selection_data['available_topics']
            surprise_number = selection_data['surprise_number']

            selected_topic = None
            parent_topic = ""
            topic_row = 0
            is_surprise = False

            # Check if it's a number
            try:
                selection = int(response)

                if selection == surprise_number:
                    # Surprise me!
                    is_surprise = True
                    # Get a random topic using the smart selection
                    selected_topic, parent_topic, topic_row = get_next_topic()
                elif 1 <= selection <= len(available_topics):
                    # Valid topic selection
                    topic_info = available_topics[selection - 1]
                    selected_topic = topic_info[0]
                    parent_topic = topic_info[1]
                    topic_row = selection + 1  # Account for header row
                else:
                    await message.reply(f"❌ Please pick a number between 1 and {surprise_number}")
                    return False

            except ValueError:
                # Not a number - check for text matches
                response_lower = response.lower()

                if 'surprise' in response_lower or response_lower == str(surprise_number):
                    is_surprise = True
                    selected_topic, parent_topic, topic_row = get_next_topic()
                else:
                    # Try to match topic names
                    for i, (topic, parent) in enumerate(available_topics):
                        if response_lower in topic.lower() or topic.lower() in response_lower:
                            selected_topic = topic
                            parent_topic = parent
                            topic_row = i + 2  # Account for header row
                            break

                    if not selected_topic:
                        await message.reply("❌ I couldn't find that topic. Please use the number or exact topic name.")
                        return False

            # Process the video recommendation
            await message.add_reaction("✅")

            if is_surprise:
                await message.reply(f"🎲 **Surprise pick: {selected_topic}!**\n⏳ Finding a great video...")
            else:
                await message.reply(f"🎯 **Great choice: {selected_topic}!**\n⏳ Finding the perfect video...")

            await self.process_video_recommendation_flow(message, selected_topic, parent_topic, topic_row, is_surprise)

            # Clean up the awaiting state
            if message.id in self.awaiting_topic_selection:
                del self.awaiting_topic_selection[message.id]

            return True

        except Exception as e:
            print(f"❌ Error handling video topic selection: {e}")
            await message.reply("❌ Something went wrong processing your selection. Try again!")
            return False

    async def process_video_recommendation_flow(self, message, topic, parent_topic, topic_row, is_surprise=False):
        """Process the complete video recommendation flow."""
        try:
            # Get feedback history
            feedback_history = get_feedback_history()
            watched_videos = get_watched_videos()

            # Search YouTube
            print(f"🔍 DEBUGGING: Searching for topic='{topic}', parent_topic='{parent_topic}'")
            all_videos = search_youtube(topic, parent_topic)
            print(f"🔍 DEBUGGING: YouTube returned {len(all_videos)} videos")

            if not all_videos:
                print(f"❌ DEBUGGING: No videos found in YouTube search")
                await message.reply(f"❌ **No videos found for '{topic}'**\n\n🎯 Let me suggest some related topics you could explore instead...")

                # Trigger topic expansion when no videos found
                await self.ask_for_topic_expansion(message.channel, topic, parent_topic)
                return

            # Filter watched videos
            print(f"🔍 DEBUGGING: Filtering {len(all_videos)} videos against {len(watched_videos)} watched URLs")
            available_videos = filter_available_videos(all_videos, watched_videos)
            print(f"🔍 DEBUGGING: {len(available_videos)} videos available after filtering")

            if not available_videos:
                print(f"❌ DEBUGGING: All videos filtered out as already watched")
                await message.reply(f"🎉 **You've watched all videos for '{topic}'!**\n\n🎯 Let me suggest some related topics to explore next...")

                # Trigger topic expansion when all videos watched
                await self.ask_for_topic_expansion(message.channel, topic, parent_topic)
                return

            # Get Claude recommendation
            recommendation = get_claude_recommendation(available_videos, topic, feedback_history)

            # Find selected video
            selected_video = None
            for video in available_videos:
                if video["video_id"] == recommendation["video_id"]:
                    selected_video = video
                    break

            if not selected_video:
                await message.reply("❌ Couldn't find the recommended video. Try again!")
                return

            # Record in Google Sheets
            record_video_recommendation(
                selected_video["title"],
                selected_video["channel_title"],
                topic,
                parent_topic,
                recommendation["video_id"],
                topic_row
            )

            # Create Discord embed
            embed = discord.Embed(
                title=selected_video["title"],
                url=f"https://www.youtube.com/watch?v={recommendation['video_id']}",
                description=recommendation["blurb"],
                color=0xFF0000
            )
            embed.set_thumbnail(url=selected_video["thumbnail_url"])

            if is_surprise:
                embed.set_footer(text=f"🎲 Surprise! • Channel: {selected_video['channel_title']} • Topic: {topic}")
            else:
                embed.set_footer(text=f"Channel: {selected_video['channel_title']} • Topic: {topic}")

            embed.add_field(
                name="Rate This Video",
                value="👍 Liked • 👎 Didn't Like • ❤️ Loved • 😴 Boring",
                inline=False
            )

            # Post video
            video_message = await message.channel.send(embed=embed)

            # Add reactions
            for emoji in ['👍', '👎', '❤️', '😴']:
                await video_message.add_reaction(emoji)

            # Store for reaction handling
            self.posted_videos[video_message.id] = {
                'video_url': f"https://www.youtube.com/watch?v={recommendation['video_id']}",
                'topic': topic,
                'video_title': selected_video["title"]
            }

            print(f"✅ Manual video posted: {selected_video['title']}")

        except Exception as e:
            print(f"❌ Error in video recommendation flow: {e}")
            await message.reply("❌ Something went wrong. Please try again!")

    async def suggest_topic_expansion(self, channel, raw_topic: str, analysis: Dict[str, Any]):
        """Suggest topic expansions when topic is already specific enough."""
        try:
            subtopics = analysis.get('specific_subtopics', [])
            intersections = analysis.get('intersection_topics', [])
            beginner_topics = analysis.get('beginner_friendly', [])
            suggested_parent = analysis.get('suggested_parent', '')

            all_suggestions = []

            # Add the original topic if specific enough
            if analysis.get('is_specific', True):
                all_suggestions.append(raw_topic)

            # Add other suggestions
            all_suggestions.extend(subtopics[:4])
            all_suggestions.extend(intersections[:2])
            all_suggestions.extend(beginner_topics[:2])

            # Remove duplicates and limit
            unique_suggestions = []
            seen = set()
            for topic in all_suggestions:
                if topic.lower() not in seen and len(unique_suggestions) < 8:
                    unique_suggestions.append(topic)
                    seen.add(topic.lower())

            topics_text = "\n".join([f"**{i+1}.** {topic}" for i, topic in enumerate(unique_suggestions)])

            message_text = f"""🎯 **Great! You want to explore '{raw_topic}'**

I've generated some related topics you might enjoy:

{topics_text}

**How to respond:**
• **Numbers**: "1 3 5" to select multiple topics
• **Topic names**: "beginner guitar chord progressions"
• **"all"**: Add all suggestions
• **Custom**: "jazz guitar theory" (your own ideas)

Which ones interest you? 🎵"""

            exploration_msg = await channel.send(message_text)

            # Track this conversation
            self.exploring_topic_interest[exploration_msg.id] = {
                'raw_topic': raw_topic,
                'analysis': analysis,
                'step': 'topic_selection',
                'suggested_topics': unique_suggestions,
                'channel_id': channel.id,
                'existing_topics': self.get_existing_topics(),
                'asked_at': datetime.now()
            }

            print(f"✅ Suggested {len(unique_suggestions)} topic expansions")

        except Exception as e:
            print(f"❌ Error suggesting topic expansion: {e}")

    async def process_topic_exploration_response(self, user_response: str, exploration_data: Dict, message) -> bool:
        """Process user's response in topic exploration conversation."""
        try:
            step = exploration_data.get('step', '')

            if step == 'parent_confirmation':
                return await self.handle_parent_confirmation(user_response, exploration_data, message)
            elif step == 'topic_selection':
                return await self.handle_exploration_topic_selection(user_response, exploration_data, message)
            else:
                print(f"❌ Unknown exploration step: {step}")
                return False

        except Exception as e:
            print(f"❌ Error processing topic exploration response: {e}")
            await message.reply("❌ There was an error processing your response. Please try again.")
            return False

    async def handle_parent_confirmation(self, user_response: str, exploration_data: Dict, message) -> bool:
        """Handle parent topic confirmation and topic selection in one message."""
        try:
            response_lower = user_response.lower().strip()
            analysis = exploration_data['analysis']
            raw_topic = exploration_data['raw_topic']

            # Parse parent topic confirmation
            confirmed_parent = analysis.get('suggested_parent', '')

            if response_lower.startswith(('yes', 'y ', 'yeah', 'yep', 'correct', 'right')):
                # Confirmed suggested parent - keep using it
                pass
            elif 'actually' in response_lower:
                # Parse alternative parent (e.g., "actually gaming, I want...")
                parent_part = response_lower.split(',')[0].replace('actually', '').strip()
                confirmed_parent = parent_part
            elif not any(word in response_lower for word in ['want', 'i', 'about', 'tips']):
                # Just a parent topic name without topic selection
                confirmed_parent = user_response.strip()
                await message.add_reaction("✅")
                await self.suggest_topic_expansion(message.channel, raw_topic, analysis)
                return True

            # Extract topics from the response
            selected_topics = []

            # Get the numbered suggestions that were shown to the user
            unique_suggestions = exploration_data.get('suggested_topics', [])

            # Parse numbers (e.g., "1 3 5")
            import re
            numbers = re.findall(r'\b(\d+)\b', user_response)
            for num_str in numbers:
                try:
                    index = int(num_str) - 1
                    if 0 <= index < len(unique_suggestions):
                        topic = unique_suggestions[index]
                        if topic not in selected_topics:
                            selected_topics.append(topic)
                except ValueError:
                    pass

            # Parse specific Overwatch-related keywords
            if 'map awareness' in response_lower:
                selected_topics.append('map awareness and positioning')
            if 'support' in response_lower and 'role' in response_lower:
                selected_topics.append('tips for playing support')
            if 'tank' in response_lower and 'role' in response_lower:
                selected_topics.append('tips for playing tank')
            if 'hero' in response_lower and any(word in response_lower for word in ['selection', 'guides', 'information']):
                selected_topics.append('hero selection and guides')

            # Clean up any exact phrases they mentioned
            response_parts = re.split(r'[,\n]|and(?:\s+the)?', user_response)
            for part in response_parts:
                part = part.strip()
                # Skip common words and already processed topics
                if (len(part) > 8 and
                    not any(skip in part.lower() for skip in ['yes', 'want', 'i', 'this is for', 'parent']) and
                    part not in selected_topics):
                    selected_topics.append(part)

            # Remove duplicates while preserving order
            final_topics = []
            for topic in selected_topics:
                if topic not in final_topics:
                    final_topics.append(topic)

            if final_topics:
                # Add the topics
                success = self.add_topics_to_sheet(final_topics, confirmed_parent)

                if success:
                    topics_text = "\n".join([f"• {topic}" for topic in final_topics])
                    await message.add_reaction("✅")
                    await message.reply(f"🎯 **Awesome! Added {len(final_topics)} topics to explore:**\n{topics_text}\n\nThese will show up in your smart topic recommendations! 🚀")

                    # Clean up the exploration state
                    if message.id in self.exploring_topic_interest:
                        del self.exploring_topic_interest[message.id]

                    return True
                else:
                    await message.reply("❌ Sorry, there was an error adding the topics. Please try again.")
                    return False
            else:
                # No topics found - proceed with generic suggestions
                await message.add_reaction("✅")
                await self.suggest_topic_expansion(message.channel, raw_topic, analysis)
                return True

        except Exception as e:
            print(f"❌ Error handling parent confirmation: {e}")
            return False

    async def handle_exploration_topic_selection(self, user_response: str, exploration_data: Dict, message) -> bool:
        """Handle topic selection in exploration conversation."""
        try:
            suggested_topics = exploration_data.get('suggested_topics', [])
            raw_topic = exploration_data['raw_topic']
            suggested_parent = exploration_data['analysis'].get('suggested_parent', raw_topic)

            selected_topics = []
            user_input = user_response.lower().strip()

            # Handle "all" selection
            if user_input in ['all', 'everything', 'all of them']:
                selected_topics = suggested_topics[:]
            else:
                # Parse numbers (1 3 5)
                numbers = [int(x) for x in user_input.split() if x.isdigit()]
                for num in numbers:
                    if 1 <= num <= len(suggested_topics):
                        topic = suggested_topics[num - 1]
                        if topic not in selected_topics:
                            selected_topics.append(topic)

                # If no numbers, try matching topic names
                if not selected_topics:
                    for suggested in suggested_topics:
                        if any(word in suggested.lower() for word in user_input.split() if len(word) > 2):
                            if suggested not in selected_topics:
                                selected_topics.append(suggested)

                    # If still no matches, treat as custom topic
                    if not selected_topics and len(user_input) > 3:
                        selected_topics.append(user_response.strip())

            if not selected_topics:
                await message.reply("❌ I couldn't understand your selection. Please try numbers (e.g. '1 3') or topic names.")
                return False

            # Add topics to Google Sheets
            success = self.add_topics_to_sheet(selected_topics, suggested_parent)

            if success:
                topics_text = "\n".join([f"• {topic}" for topic in selected_topics])
                await message.add_reaction("✅")
                await message.reply(f"🎯 **Awesome! Added {len(selected_topics)} topics to explore:**\n{topics_text}\n\nThese will show up in your smart topic recommendations! 🚀")
                return True
            else:
                await message.reply("❌ Sorry, there was an error adding the topics. Please try again.")
                return False

        except Exception as e:
            print(f"❌ Error handling exploration topic selection: {e}")
            return False

    async def post_video_recommendation(self, video_id: str, blurb: str, videos: List[Dict[str, Any]], topic: str):
        """Post a video recommendation to Discord with feedback emoji buttons."""
        print("📤 Posting to Discord...")

        # Find the video details
        selected_video = None
        for video in videos:
            if video["video_id"] == video_id:
                selected_video = video
                break

        if not selected_video:
            print(f"❌ Could not find video with ID {video_id}")
            return

        try:
            # Get the target channel
            channel = self.client.get_channel(DISCORD_CHANNEL_ID)
            if not channel:
                print(f"❌ Could not find channel with ID {DISCORD_CHANNEL_ID}")
                return

            # Create Discord embed
            embed = discord.Embed(
                title=selected_video["title"],
                url=f"https://www.youtube.com/watch?v={video_id}",
                description=blurb,
                color=0xFF0000  # YouTube red
            )
            embed.set_thumbnail(url=selected_video["thumbnail_url"])
            embed.set_footer(text=f"Channel: {selected_video['channel_title']} • Topic: {topic}")

            # Add feedback instructions
            embed.add_field(
                name="Rate This Video",
                value="👍 Liked • 👎 Didn't Like • ❤️ Loved • 😴 Boring",
                inline=False
            )

            # Send the embed
            message = await channel.send(embed=embed)

            # Store video info for later reference
            self.posted_videos[message.id] = {
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'topic': topic,
                'video_title': selected_video["title"]
            }

            # Add reaction emojis as buttons
            for emoji in FEEDBACK_EMOJIS.keys():
                await message.add_reaction(emoji)

            print("✅ Posted to Discord with feedback buttons!")

        except Exception as e:
            print(f"❌ Error posting to Discord: {e}")

    async def start(self):
        """Start the Discord bot."""
        await self.client.start(DISCORD_BOT_TOKEN)

async def daily_job_mode():
    """Daily scheduled job mode: find topic, get recommendation, post to Discord, then exit cleanly."""
    print("🎯 Daily Job Mode: Starting workflow...")

    try:
        # Validate environment
        validate_environment()

        # Get feedback history to improve recommendations
        feedback_history = get_feedback_history()

        # Get watched/pending videos to avoid duplicates
        watched_videos = get_watched_videos()

        # Get next topic from Google Sheets
        topic, parent_topic, topic_row = get_next_topic()
        print(f"📌 Topic: {topic}")

        # Search YouTube
        all_videos = search_youtube(topic, parent_topic)

        # Filter out already watched/pending videos
        available_videos = filter_available_videos(all_videos, watched_videos)

        if not available_videos:
            print("❌ No new videos found for this topic - initiating topic expansion")
            # For daily mode, we'll just log this and exit - topic expansion requires user interaction
            print("💡 Consider adding more topics to your Google Sheet or marking some videos as watched")
            return

        # Get Claude's recommendation from available videos only (with feedback history)
        recommendation = get_claude_recommendation(available_videos, topic, feedback_history)

        # Find the selected video for recording
        selected_video = None
        for video in available_videos:
            if video["video_id"] == recommendation["video_id"]:
                selected_video = video
                break

        if not selected_video:
            print(f"❌ Could not find video with ID {recommendation['video_id']}")
            return

        # Record the recommendation in Google Sheets
        record_video_recommendation(
            selected_video["title"],
            selected_video["channel_title"],
            topic,
            parent_topic,
            recommendation["video_id"],
            topic_row
        )

        # Initialize bot for posting
        bot = HobbyMaxxingBot()

        # Use a task to start bot briefly
        bot_task = asyncio.create_task(bot.start())

        # Wait for bot to be ready
        await asyncio.sleep(3)

        try:
            # Get the target channel
            channel = bot.client.get_channel(DISCORD_CHANNEL_ID)
            if not channel:
                print(f"❌ Could not find channel with ID {DISCORD_CHANNEL_ID}")
                return

            # Create Discord embed
            embed = discord.Embed(
                title=selected_video["title"],
                url=f"https://www.youtube.com/watch?v={recommendation['video_id']}",
                description=recommendation["blurb"],
                color=0xFF0000  # YouTube red
            )
            embed.set_thumbnail(url=selected_video["thumbnail_url"])
            embed.set_footer(text=f"Channel: {selected_video['channel_title']} • Topic: {topic}")

            # Add feedback instructions
            embed.add_field(
                name="Rate This Video",
                value="👍 Liked • 👎 Didn't Like • ❤️ Loved • 😴 Boring",
                inline=False
            )

            # Send the embed
            message = await channel.send(embed=embed)

            # Add reaction emojis as buttons
            feedback_emojis = ['👍', '👎', '❤️', '😴']
            for emoji in feedback_emojis:
                await message.add_reaction(emoji)

            print("✅ Video recommendation posted to Discord!")
            print("🎯 Daily job complete - exiting cleanly.")

        finally:
            # Clean up the bot task
            if not bot_task.done():
                bot_task.cancel()
                try:
                    await bot_task
                except asyncio.CancelledError:
                    pass

            # Ensure Discord client is closed
            if not bot.client.is_closed():
                await bot.client.close()

    except Exception as e:
        print(f"❌ Error in daily job mode: {e}")
        import traceback
        traceback.print_exc()

async def github_daily_job_mode():
    """GitHub Actions daily job mode: identical to daily_job_mode but with additional logging."""
    print("🐙 GitHub Actions Mode: Starting workflow...")

    # GitHub Actions mode is identical to daily job mode, just with different logging
    await daily_job_mode()

    print("🐙 GitHub Actions job complete!")

async def listen_mode():
    """Persistent listener mode: handle Discord reactions, notes, and topic exploration only."""
    print("👂 Listen Mode: Starting persistent Discord bot...")

    try:
        # Validate environment
        validate_environment()

        # Initialize the Discord bot
        bot = HobbyMaxxingBot()

        print("✅ Bot initialized - starting persistent listening...")
        print("👍 👎 ❤️ 😴 React to messages to give feedback!")
        print("💬 Chat naturally to explore new topic interests!")
        print("Press Ctrl+C to stop the bot.")

        # Start the bot and run indefinitely
        await bot.start()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down listener...")
        if 'bot' in locals() and hasattr(bot, 'client'):
            await bot.client.close()
    except Exception as e:
        print(f"❌ Error in listen mode: {e}")
        if 'bot' in locals() and hasattr(bot, 'client'):
            await bot.client.close()

async def railway_listener_mode():
    """Railway listener mode: minimal persistent bot for cloud deployment."""
    print("🚂 Railway Listener Mode: Starting minimal cloud listener...")

    # Railway listener mode is identical to listen mode for now
    await listen_mode()

async def main():
    """Main execution flow with persistent bot for feedback."""
    print("🎯 YouTube Hobby Maxxxer MVP Starting...")

    # Validate environment
    validate_environment()

    # Initialize the Discord bot
    bot = HobbyMaxxingBot()

    try:
        # Get feedback history to improve recommendations
        feedback_history = get_feedback_history()

        # Get watched/pending videos to avoid duplicates
        watched_videos = get_watched_videos()

        # Get next topic from Google Sheets
        topic, parent_topic, topic_row = get_next_topic()
        print(f"📌 Topic: {topic}")

        # Search YouTube
        all_videos = search_youtube(topic, parent_topic)

        # Filter out already watched/pending videos
        available_videos = filter_available_videos(all_videos, watched_videos)

        if not available_videos:
            print("❌ No new videos found for this topic - all have been watched or are pending")
            print("🤔 Initiating topic expansion flow...")

            # Start Discord bot first to handle topic expansion
            bot_task = asyncio.create_task(bot.start())

            # Wait a moment for bot to connect
            await asyncio.sleep(2)

            # Ask for topic expansion instead of giving up
            await bot.ask_for_topic_expansion(
                bot.client.get_channel(DISCORD_CHANNEL_ID),
                topic,
                parent_topic
            )

            print("✅ Asked for topic expansion! Bot will continue running to handle your response.")
            print("📝 Reply with topic numbers or names to explore new areas!")
            print("Press Ctrl+C to stop the bot.")

            # Keep the bot running to handle topic selection
            await bot_task
            return

        # Get Claude's recommendation from available videos only (with feedback history)
        recommendation = get_claude_recommendation(available_videos, topic, feedback_history)

        # Find the selected video for recording
        selected_video = None
        for video in available_videos:
            if video["video_id"] == recommendation["video_id"]:
                selected_video = video
                break

        if not selected_video:
            print(f"❌ Could not find video with ID {recommendation['video_id']}")
            return

        # Record the recommendation in Google Sheets
        record_video_recommendation(
            selected_video["title"],
            selected_video["channel_title"],
            topic,
            parent_topic,
            recommendation["video_id"],
            topic_row
        )

        print("🎉 Video selected and recorded!")
        print("🤖 Starting Discord bot to post recommendation and listen for feedback...")

        # Start Discord bot in the background
        bot_task = asyncio.create_task(bot.start())

        # Wait a moment for bot to connect
        await asyncio.sleep(2)

        # Post the recommendation with feedback buttons
        await bot.post_video_recommendation(
            recommendation["video_id"],
            recommendation["blurb"],
            available_videos,
            topic
        )

        print("✅ Posted to Discord! Bot will continue running to collect feedback.")
        print("👍 👎 ❤️ 😴 React to the message to give feedback!")
        print("Press Ctrl+C to stop the bot.")

        # Wait for workflow completion with timeout
        print(f"⏰ Bot will auto-shutdown in {bot.shutdown_timeout_hours} hours if no feedback is received")

        # Conditional waiting with timeout and shutdown checks
        timeout_seconds = bot.shutdown_timeout_hours * 3600  # Convert hours to seconds
        start_time = asyncio.get_event_loop().time()

        while not bot.should_shutdown:
            # Check for timeout
            if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                print(f"⏰ Timeout reached ({bot.shutdown_timeout_hours}h) - shutting down gracefully")
                bot.should_shutdown = True
                break

            # Wait a bit before checking again (non-blocking)
            try:
                await asyncio.wait_for(asyncio.sleep(5), timeout=1.0)
            except asyncio.TimeoutError:
                pass  # Continue the loop

            # Check if the bot task has failed
            if bot_task.done():
                exception = bot_task.exception()
                if exception:
                    print(f"❌ Bot task failed: {exception}")
                    break
                else:
                    print("✅ Bot task completed normally")
                    break

        # Clean shutdown
        if bot.workflow_complete:
            print("🏁 Workflow completed successfully!")
        else:
            print("🛑 Shutting down due to timeout or interruption")

        # Cancel the bot task if it's still running
        if not bot_task.done():
            print("🧹 Cleaning up bot task...")
            bot_task.cancel()
            try:
                await bot_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling

        # Ensure Discord client is closed
        if not bot.client.is_closed():
            await bot.client.close()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down bot...")
        await bot.client.close()
    except Exception as e:
        print(f"❌ Error: {e}")
        if bot.client:
            await bot.client.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Hobby Maxxxer - AI-powered hobby video recommendations")
    parser.add_argument("--daily-job", action="store_true",
                       help="Run daily job: find topic, get recommendation, post to Discord, then exit")
    parser.add_argument("--listen", action="store_true",
                       help="Run persistent listener: handle Discord reactions, notes, and topic exploration")
    parser.add_argument("--github-daily-job", action="store_true",
                       help="GitHub Actions mode: run daily job and exit immediately (no waiting)")
    parser.add_argument("--railway-listener", action="store_true",
                       help="Railway mode: minimal persistent listener for cloud deployment")

    args = parser.parse_args()

    try:
        # Add startup delay to prevent rapid restart loops on Railway
        import time
        import os
        if os.getenv("RAILWAY_ENVIRONMENT"):
            print("🚂 Detected Railway environment, adding startup delay...")
            time.sleep(5)

        if args.daily_job:
            print("🕘 Starting daily job mode...")
            asyncio.run(daily_job_mode())
        elif args.listen:
            print("👂 Starting listen mode...")
            asyncio.run(listen_mode())
        elif args.github_daily_job:
            print("🐙 Starting GitHub Actions daily job mode...")
            asyncio.run(github_daily_job_mode())
        elif args.railway_listener:
            print("🚂 Starting Railway listener mode...")
            asyncio.run(railway_listener_mode())
        else:
            print("🎯 Starting single-run mode (current behavior)...")

            # For Railway, we probably want to run the listener instead of single-run
            if os.getenv("RAILWAY_ENVIRONMENT"):
                print("🚂 Railway detected: switching to listener mode for persistent deployment")
                asyncio.run(railway_listener_mode())
            else:
                asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

        # On Railway, wait before exiting to prevent rapid restart loops
        if os.getenv("RAILWAY_ENVIRONMENT"):
            print("⏱️  Waiting 30 seconds before exit to prevent rapid restarts...")
            time.sleep(30)