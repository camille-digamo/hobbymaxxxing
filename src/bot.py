"""
Main HobbyMaxxingBot class - Discord bot for video recommendations and learning
"""

import discord
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import re
import random

from .utils import DISCORD_USER_ID, DISCORD_CHANNEL_ID, DISCORD_BOT_TOKEN, FEEDBACK_EMOJIS
from .discord_service import (
    create_discord_client,
    create_video_embed,
    extract_video_info_from_embed,
    detect_video_request_pattern,
    create_topic_selection_message,
    parse_topic_selection,
    add_feedback_reactions,
    get_feedback_from_reaction,
    extract_notes_from_reply,
    should_ignore_message
)
from .youtube_service import search_youtube, filter_available_videos
from .claude_service import get_claude_recommendation, analyze_topic_interest, generate_topic_expansion
from .sheets_service import (
    get_next_topic,
    get_watched_videos,
    get_feedback_history,
    record_video_recommendation,
    update_video_feedback,
    update_video_notes
)


class HobbyMaxxingBot:
    """Persistent Discord bot that handles video recommendations and feedback."""

    def __init__(self):
        # Initialize Discord client
        self.client = create_discord_client()

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

            # Check if we should ignore this message
            if should_ignore_message(message, self.client.user, DISCORD_USER_ID):
                print("⏭️  Ignoring message")
                return

            await self.handle_user_message(message)

        @self.client.event
        async def on_reaction_add(reaction, user):
            """Handle feedback reactions."""
            if user.id != DISCORD_USER_ID or user == self.client.user:
                return

            await self.handle_feedback_reaction(reaction, user)

    async def run(self):
        """Start the Discord bot."""
        await self.client.start(DISCORD_BOT_TOKEN)

    async def close(self):
        """Gracefully close the Discord client."""
        if not self.client.is_closed():
            await self.client.close()
            print("✅ Discord client closed")

    # Placeholder methods - to be implemented
    async def handle_user_message(self, message):
        """Handle incoming user messages - placeholder for modular implementation."""
        pass

    async def handle_feedback_reaction(self, reaction, user):
        """Handle feedback reactions - placeholder for modular implementation."""
        pass