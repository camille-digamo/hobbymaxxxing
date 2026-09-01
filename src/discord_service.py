"""
Discord bot integration for user interactions and message handling
"""

import discord
from discord.ext import commands
import re
import random
from typing import List, Optional, Dict, Any
from .utils import (
    DISCORD_BOT_TOKEN,
    DISCORD_CHANNEL_ID,
    DISCORD_USER_ID,
    FEEDBACK_EMOJIS
)


def create_discord_client():
    """Create and configure Discord client with proper intents."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    return discord.Client(intents=intents)


def create_video_embed(video_title: str, channel: str, video_url: str, blurb: str, topic: str, parent_topic: str = "") -> discord.Embed:
    """Create rich embed for video recommendations."""
    # Create embed with video info
    embed = discord.Embed(
        title=video_title,
        url=video_url,
        description=blurb,
        color=0x00ff00
    )

    # Add fields
    embed.add_field(name="Channel", value=channel, inline=True)

    topic_display = f"{topic} ({parent_topic})" if parent_topic else topic
    embed.add_field(name="Topic", value=topic_display, inline=True)

    # Footer with instructions
    embed.set_footer(text="React with 👍👎❤️💤 to give feedback, or reply with notes!")

    return embed


def extract_video_info_from_embed(embed: discord.Embed) -> Optional[Dict[str, str]]:
    """Extract video information from Discord embed for cross-process communication."""
    if not embed or not embed.url:
        return None

    # Extract basic info from embed
    video_info = {
        'video_url': embed.url,
        'video_title': embed.title or '',
        'channel': '',
        'topic': '',
        'parent_topic': ''
    }

    # Extract from fields
    for field in embed.fields:
        if field.name == "Channel":
            video_info['channel'] = field.value
        elif field.name == "Topic":
            topic_value = field.value
            if '(' in topic_value and ')' in topic_value:
                # Extract topic and parent_topic from "topic (parent_topic)" format
                parts = topic_value.split('(')
                video_info['topic'] = parts[0].strip()
                video_info['parent_topic'] = parts[1].rstrip(')').strip()
            else:
                video_info['topic'] = topic_value

    return video_info


def detect_video_request_pattern(message_content: str) -> bool:
    """Detect if a Discord message is requesting a video recommendation."""
    content = message_content.lower().strip()

    # Natural language patterns for video requests
    request_patterns = [
        r"can you recommend me something",
        r"can you send me a video",
        r"i need something to watch",
        r"recommend something",
        r"send me something",
        r"suggest a video",
        r"what should i watch",
        r"give me a video",
        r"show me something",
        r"pick something for me",
        r"surprise me",
        r"recommend a video",
        r"i want to learn",
        r"teach me about",
        r"help me learn"
    ]

    return any(re.search(pattern, content) for pattern in request_patterns)


def create_topic_selection_message(topics: List[str]) -> str:
    """Create a formatted message for topic selection."""
    if not topics:
        return "No topics available right now. Try asking me to explore a new topic!"

    message = "**Choose a topic to learn about:**\n\n"

    # Add numbered topics (limit to 10 for readability)
    display_topics = topics[:10]
    for i, topic in enumerate(display_topics, 1):
        message += f"{i}. {topic}\n"

    # Add surprise option
    message += f"{len(display_topics) + 1}. 🎲 **Surprise me!** (random topic)\n"
    message += f"\nReply with the number of your choice (1-{len(display_topics) + 1})"

    return message


def parse_topic_selection(message_content: str, available_topics: List[str]) -> Optional[str]:
    """Parse user's topic selection from numbered list."""
    content = message_content.strip()

    try:
        # Try to parse as number
        choice_num = int(content)

        # Check if it's the "surprise me" option
        if choice_num == len(available_topics) + 1:
            return "SURPRISE_ME"

        # Check if it's a valid topic number
        if 1 <= choice_num <= len(available_topics):
            return available_topics[choice_num - 1]

    except ValueError:
        # Not a number, maybe they typed the topic name
        content_lower = content.lower()
        for topic in available_topics:
            if topic.lower() in content_lower or content_lower in topic.lower():
                return topic

    return None


def create_topic_exploration_embed(topic: str, parent_topic: str, suggested_topics: List[str]) -> discord.Embed:
    """Create embed for topic exploration suggestions."""
    embed = discord.Embed(
        title=f"🎯 Exploring: {topic}",
        description=f"Great choice! Here are some specific areas you could dive into:",
        color=0x3498db
    )

    if parent_topic:
        embed.add_field(name="Category", value=parent_topic, inline=True)

    # Add suggested topics as a formatted list
    if suggested_topics:
        topics_text = "\n".join([f"• {t}" for t in suggested_topics[:8]])
        embed.add_field(name="Suggested Topics", value=topics_text, inline=False)

    embed.set_footer(text="I'll add these to your learning topics! You can always ask for recommendations on any of these.")

    return embed


async def add_feedback_reactions(message: discord.Message):
    """Add feedback reaction emojis to a message."""
    try:
        for emoji in FEEDBACK_EMOJIS.keys():
            await message.add_reaction(emoji)
        print("✅ Added feedback reactions")
    except Exception as e:
        print(f"❌ Error adding reactions: {e}")


def get_feedback_from_reaction(emoji: str) -> Optional[str]:
    """Convert reaction emoji to feedback string."""
    return FEEDBACK_EMOJIS.get(emoji)


def extract_notes_from_reply(message_content: str) -> str:
    """Extract and clean notes from user reply."""
    # Remove common prefixes that aren't part of the actual notes
    prefixes_to_remove = [
        "notes:",
        "note:",
        "my notes:",
        "here are my notes:",
        "notes about this video:",
    ]

    content = message_content.strip()
    content_lower = content.lower()

    for prefix in prefixes_to_remove:
        if content_lower.startswith(prefix):
            content = content[len(prefix):].strip()
            break

    return content


def is_bot_mention(message: discord.Message, bot_user: discord.User) -> bool:
    """Check if message mentions the bot."""
    return bot_user in message.mentions


def should_ignore_message(message: discord.Message, bot_user: discord.User, target_user_id: int) -> bool:
    """Determine if bot should ignore a message."""
    # Ignore own messages
    if message.author.id == bot_user.id:
        return True

    # Only respond to target user
    if message.author.id != target_user_id:
        return True

    # Only respond in the designated channel
    if message.channel.id != DISCORD_CHANNEL_ID:
        return True

    return False