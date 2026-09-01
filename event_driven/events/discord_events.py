"""
Discord-related events for the YouTube Hobby Maxxxer.

These events handle Discord UI interactions, messages, and reactions.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.event_bus import Event


@dataclass
class DiscordMessageReceived(Event):
    """Event: Message received from Discord user"""
    event_type: str = "discord.message_received"
    message_id: int = 0
    channel_id: int = 0
    user_id: int = 0
    username: str = ""
    content: str = ""
    is_bot_response: bool = False
    is_authorized_user: bool = False


@dataclass
class DiscordReactionAdded(Event):
    """Event: User added reaction to a message"""
    event_type: str = "discord.reaction_added"
    message_id: int = 0
    channel_id: int = 0
    user_id: int = 0
    emoji: str = ""
    is_authorized_user: bool = False
    is_feedback_emoji: bool = False


@dataclass
class DiscordPostRequested(Event):
    """Event: Request to post video recommendation to Discord"""
    event_type: str = "discord.post_requested"
    video_id: str = ""
    video_title: str = ""
    video_url: str = ""
    channel_title: str = ""
    thumbnail_url: str = ""
    blurb: str = ""
    topic: str = ""
    discord_channel_id: int = 0


@dataclass
class DiscordMessagePosted(Event):
    """Event: Message successfully posted to Discord"""
    event_type: str = "discord.message_posted"
    message_id: int = 0
    channel_id: int = 0
    video_url: str = ""
    video_title: str = ""
    topic: str = ""
    reactions_added: bool = False


@dataclass
class DiscordEmbedUpdateRequested(Event):
    """Event: Request to update Discord embed with feedback"""
    event_type: str = "discord.embed_update_requested"
    message_id: int = 0
    channel_id: int = 0
    feedback_type: str = ""
    feedback_emoji: str = ""
    status_message: str = ""


@dataclass
class DiscordFeedbackReceived(Event):
    """Event: User feedback received via Discord reaction"""
    event_type: str = "discord.feedback_received"
    video_url: str = ""
    video_title: str = ""
    feedback: str = ""  # liked, loved, didn't_like, boring
    feedback_emoji: str = ""
    topic: str = ""
    user_id: int = 0
    message_id: int = 0
    date_received: str = ""


@dataclass
class DiscordNotesPromptRequested(Event):
    """Event: Request to prompt user for video notes"""
    event_type: str = "discord.notes_prompt_requested"
    video_url: str = ""
    video_title: str = ""
    topic: str = ""
    channel_id: int = 0
    original_message_id: int = 0


@dataclass
class DiscordNotesPromptPosted(Event):
    """Event: Notes prompt successfully posted to Discord"""
    event_type: str = "discord.notes_prompt_posted"
    notes_message_id: int = 0
    original_message_id: int = 0
    channel_id: int = 0
    video_url: str = ""
    video_title: str = ""
    topic: str = ""
    awaiting_response: bool = True


@dataclass
class DiscordTopicExpansionRequested(Event):
    """Event: Request to post topic expansion options to Discord"""
    event_type: str = "discord.topic_expansion_requested"
    original_topic: str = ""
    suggested_topics: list = None
    suggested_parent: str = ""
    channel_id: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.suggested_topics is None:
            self.suggested_topics = []


@dataclass
class DiscordTopicExpansionPosted(Event):
    """Event: Topic expansion options posted to Discord"""
    event_type: str = "discord.topic_expansion_posted"
    expansion_message_id: int = 0
    channel_id: int = 0
    original_topic: str = ""
    suggested_topics: list = None
    awaiting_selection: bool = True

    def __post_init__(self):
        super().__post_init__()
        if self.suggested_topics is None:
            self.suggested_topics = []


@dataclass
class DiscordTopicSelectionReceived(Event):
    """Event: User has selected topics from expansion"""
    event_type: str = "discord.topic_selection_received"
    user_response: str = ""
    selected_topics: list = None
    parent_topic: str = ""
    message_id: int = 0
    channel_id: int = 0
    user_id: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.selected_topics is None:
            self.selected_topics = []


@dataclass
class DiscordInterestConfirmationRequested(Event):
    """Event: Request confirmation of topic interest from user"""
    event_type: str = "discord.interest_confirmation_requested"
    refined_topic: str = ""
    parent_topic: str = ""
    suggested_related: list = None
    channel_id: int = 0
    original_message_id: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.suggested_related is None:
            self.suggested_related = []


@dataclass
class DiscordInterestConfirmationPosted(Event):
    """Event: Interest confirmation posted to Discord"""
    event_type: str = "discord.interest_confirmation_posted"
    confirmation_message_id: int = 0
    channel_id: int = 0
    refined_topic: str = ""
    awaiting_response: bool = True


@dataclass
class DiscordInterestConfirmed(Event):
    """Event: User confirmed their topic interest"""
    event_type: str = "discord.interest_confirmed"
    confirmed_topic: str = ""
    parent_topic: str = ""
    additional_topics: list = None
    user_response: str = ""
    message_id: int = 0
    user_id: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.additional_topics is None:
            self.additional_topics = []


@dataclass
class DiscordErrorOccurred(Event):
    """Event: Discord-related error occurred"""
    event_type: str = "discord.error_occurred"
    error_type: str = ""
    error_message: str = ""
    channel_id: int = 0
    message_id: int = 0
    context: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.context is None:
            self.context = {}


# Helper functions for creating common Discord events

def create_discord_post_request(video_data: Dict[str, Any], blurb: str, topic: str,
                               channel_id: int, session_id: str = None,
                               user_id: str = None) -> DiscordPostRequested:
    """Create a Discord post request event"""
    return DiscordPostRequested(
        video_id=video_data.get("video_id", ""),
        video_title=video_data.get("title", ""),
        video_url=video_data.get("video_url", ""),
        channel_title=video_data.get("channel_title", ""),
        thumbnail_url=video_data.get("thumbnail_url", ""),
        blurb=blurb,
        topic=topic,
        discord_channel_id=channel_id,
        session_id=session_id,
        user_id=user_id
    )


def create_discord_feedback_event(video_url: str, video_title: str, feedback: str,
                                emoji: str, topic: str, user_id: int, message_id: int,
                                session_id: str = None) -> DiscordFeedbackReceived:
    """Create a Discord feedback received event"""
    return DiscordFeedbackReceived(
        video_url=video_url,
        video_title=video_title,
        feedback=feedback,
        feedback_emoji=emoji,
        topic=topic,
        user_id=user_id,
        message_id=message_id,
        date_received=datetime.now().strftime("%Y/%m/%d"),
        session_id=session_id,
        user_id=str(user_id)
    )


def create_discord_message_event(message_id: int, channel_id: int, user_id: int,
                                username: str, content: str, is_authorized: bool = False,
                                session_id: str = None) -> DiscordMessageReceived:
    """Create a Discord message received event"""
    return DiscordMessageReceived(
        message_id=message_id,
        channel_id=channel_id,
        user_id=user_id,
        username=username,
        content=content,
        is_authorized_user=is_authorized,
        session_id=session_id,
        user_id=str(user_id)
    )