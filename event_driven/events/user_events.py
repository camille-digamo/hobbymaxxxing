"""
User-related events for the YouTube Hobby Maxxxer.

These events handle user sessions, preferences, and interactions.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.event_bus import Event


@dataclass
class UserSessionStarted(Event):
    """Event: User has started a new session"""
    event_type: str = "user.session_started"
    user_discord_id: int = 0
    username: str = ""
    session_type: str = "interactive"  # interactive, daily_job, topic_exploration
    initial_context: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.initial_context is None:
            self.initial_context = {}


@dataclass
class UserSessionEnded(Event):
    """Event: User session has ended"""
    event_type: str = "user.session_ended"
    user_discord_id: int = 0
    session_duration_seconds: float = 0.0
    interactions_count: int = 0
    completion_reason: str = "normal"  # normal, timeout, error, user_exit


@dataclass
class UserPreferencesRequested(Event):
    """Event: Request for user preferences and history"""
    event_type: str = "user.preferences_requested"
    user_discord_id: int = 0
    preference_types: list = None

    def __post_init__(self):
        super().__post_init__()
        if self.preference_types is None:
            self.preference_types = ["feedback_history", "topic_interests", "viewing_patterns"]


@dataclass
class UserPreferencesLoaded(Event):
    """Event: User preferences have been loaded from storage"""
    event_type: str = "user.preferences_loaded"
    user_discord_id: int = 0
    feedback_history: Dict[str, Any] = None
    topic_interests: Dict[str, float] = None
    viewing_patterns: Dict[str, Any] = None
    total_videos_watched: int = 0
    account_created: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.feedback_history is None:
            self.feedback_history = {}
        if self.topic_interests is None:
            self.topic_interests = {}
        if self.viewing_patterns is None:
            self.viewing_patterns = {}


@dataclass
class UserFeedbackUpdated(Event):
    """Event: User feedback patterns have been updated"""
    event_type: str = "user.feedback_updated"
    user_discord_id: int = 0
    video_url: str = ""
    feedback_type: str = ""
    previous_feedback: str = ""
    updated_patterns: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.updated_patterns is None:
            self.updated_patterns = {}


@dataclass
class UserInteractionRecorded(Event):
    """Event: User interaction has been recorded"""
    event_type: str = "user.interaction_recorded"
    user_discord_id: int = 0
    interaction_type: str = ""  # message, reaction, topic_selection, notes
    interaction_data: Dict[str, Any] = None
    response_time_seconds: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        if self.interaction_data is None:
            self.interaction_data = {}


@dataclass
class UserStateUpdated(Event):
    """Event: User session state has been updated"""
    event_type: str = "user.state_updated"
    user_discord_id: int = 0
    state_key: str = ""
    previous_value: Any = None
    new_value: Any = None
    update_reason: str = ""


@dataclass
class UserOnboardingStarted(Event):
    """Event: New user onboarding process started"""
    event_type: str = "user.onboarding_started"
    user_discord_id: int = 0
    username: str = ""
    onboarding_step: str = "welcome"
    estimated_duration_minutes: int = 5


@dataclass
class UserOnboardingCompleted(Event):
    """Event: User onboarding process completed"""
    event_type: str = "user.onboarding_completed"
    user_discord_id: int = 0
    completion_time_minutes: float = 0.0
    steps_completed: list = None
    initial_topics_added: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.steps_completed is None:
            self.steps_completed = []


@dataclass
class UserActivitySummaryRequested(Event):
    """Event: Request for user activity summary"""
    event_type: str = "user.activity_summary_requested"
    user_discord_id: int = 0
    period_days: int = 30
    include_recommendations: bool = True
    include_feedback: bool = True


@dataclass
class UserActivitySummaryGenerated(Event):
    """Event: User activity summary has been generated"""
    event_type: str = "user.activity_summary_generated"
    user_discord_id: int = 0
    summary_period: str = ""
    videos_recommended: int = 0
    videos_watched: int = 0
    feedback_given: int = 0
    topics_explored: int = 0
    favorite_topics: list = None
    activity_trends: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.favorite_topics is None:
            self.favorite_topics = []
        if self.activity_trends is None:
            self.activity_trends = {}


@dataclass
class UserLearningMilestone(Event):
    """Event: User has reached a learning milestone"""
    event_type: str = "user.learning_milestone"
    user_discord_id: int = 0
    milestone_type: str = ""  # first_video, tenth_video, first_notes, topic_master
    milestone_description: str = ""
    achievement_date: str = ""
    celebration_message: str = ""

    def __post_init__(self):
        super().__post_init__()
        if not self.achievement_date:
            self.achievement_date = datetime.now().strftime("%Y-%m-%d")


# Helper functions for creating common user events

def create_user_session_start(discord_id: int, username: str, session_type: str = "interactive",
                            context: Dict[str, Any] = None) -> UserSessionStarted:
    """Create a user session started event"""
    return UserSessionStarted(
        user_discord_id=discord_id,
        username=username,
        session_type=session_type,
        initial_context=context or {},
        user_id=str(discord_id)
    )


def create_user_preferences_request(discord_id: int,
                                  preference_types: list = None) -> UserPreferencesRequested:
    """Create a user preferences request event"""
    return UserPreferencesRequested(
        user_discord_id=discord_id,
        preference_types=preference_types,
        user_id=str(discord_id)
    )


def create_user_feedback_update(discord_id: int, video_url: str, feedback_type: str,
                              previous_feedback: str = "",
                              updated_patterns: Dict[str, Any] = None) -> UserFeedbackUpdated:
    """Create a user feedback updated event"""
    return UserFeedbackUpdated(
        user_discord_id=discord_id,
        video_url=video_url,
        feedback_type=feedback_type,
        previous_feedback=previous_feedback,
        updated_patterns=updated_patterns or {},
        user_id=str(discord_id)
    )


def create_user_interaction_record(discord_id: int, interaction_type: str,
                                 interaction_data: Dict[str, Any] = None,
                                 response_time: float = 0.0) -> UserInteractionRecorded:
    """Create a user interaction recorded event"""
    return UserInteractionRecorded(
        user_discord_id=discord_id,
        interaction_type=interaction_type,
        interaction_data=interaction_data or {},
        response_time_seconds=response_time,
        user_id=str(discord_id)
    )