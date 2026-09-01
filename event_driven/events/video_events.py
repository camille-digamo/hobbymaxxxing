"""
Video-related events for the YouTube Hobby Maxxxer.

These events handle the video recommendation workflow:
searching, filtering, recommendation, and recording.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.event_bus import Event


@dataclass
class VideoSearchRequested(Event):
    """Event: Request to search YouTube for videos on a topic"""
    event_type: str = "video.search_requested"
    topic: str = ""
    parent_topic: str = ""
    max_results: int = 8
    feedback_history: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.feedback_history is None:
            self.feedback_history = {}


@dataclass
class VideoSearchCompleted(Event):
    """Event: YouTube search completed with results"""
    event_type: str = "video.search_completed"
    topic: str = ""
    videos: List[Dict[str, Any]] = None
    total_found: int = 0
    available_count: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.videos is None:
            self.videos = []


@dataclass
class VideoFilterRequested(Event):
    """Event: Request to filter videos against watched history"""
    event_type: str = "video.filter_requested"
    videos: List[Dict[str, Any]] = None
    topic: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.videos is None:
            self.videos = []


@dataclass
class VideoFilterCompleted(Event):
    """Event: Video filtering completed"""
    event_type: str = "video.filter_completed"
    available_videos: List[Dict[str, Any]] = None
    filtered_count: int = 0
    original_count: int = 0
    topic: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.available_videos is None:
            self.available_videos = []


@dataclass
class VideoRecommendationRequested(Event):
    """Event: Request Claude AI recommendation from filtered videos"""
    event_type: str = "video.recommendation_requested"
    available_videos: List[Dict[str, Any]] = None
    topic: str = ""
    parent_topic: str = ""
    feedback_history: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.available_videos is None:
            self.available_videos = []
        if self.feedback_history is None:
            self.feedback_history = {}


@dataclass
class VideoRecommended(Event):
    """Event: Claude AI has selected a video recommendation"""
    event_type: str = "video.recommended"
    video_id: str = ""
    video_title: str = ""
    channel_title: str = ""
    video_url: str = ""
    thumbnail_url: str = ""
    blurb: str = ""
    reasoning: str = ""
    topic: str = ""
    parent_topic: str = ""

    def __post_init__(self):
        super().__post_init__()
        if not self.video_url and self.video_id:
            self.video_url = f"https://www.youtube.com/watch?v={self.video_id}"


@dataclass
class VideoRecommendationFailed(Event):
    """Event: Video recommendation process failed"""
    event_type: str = "video.recommendation_failed"
    topic: str = ""
    error_type: str = ""
    error_message: str = ""
    retry_count: int = 0


@dataclass
class VideoRecordRequested(Event):
    """Event: Request to record video recommendation in Google Sheets"""
    event_type: str = "video.record_requested"
    video_title: str = ""
    channel_title: str = ""
    video_url: str = ""
    video_id: str = ""
    topic: str = ""
    parent_topic: str = ""
    topic_row: int = 0


@dataclass
class VideoRecorded(Event):
    """Event: Video recommendation successfully recorded"""
    event_type: str = "video.recorded"
    video_title: str = ""
    video_url: str = ""
    topic: str = ""
    sheet_row: int = 0
    date_recommended: str = ""


@dataclass
class VideoWatched(Event):
    """Event: User has watched/rated a video"""
    event_type: str = "video.watched"
    video_url: str = ""
    video_title: str = ""
    rating: str = ""  # liked, loved, didn't_like, boring
    feedback_emoji: str = ""
    topic: str = ""
    date_watched: str = ""


@dataclass
class VideoNotesRequested(Event):
    """Event: Request user notes for a video"""
    event_type: str = "video.notes_requested"
    video_url: str = ""
    video_title: str = ""
    topic: str = ""
    discord_channel_id: int = 0
    discord_message_id: int = 0


@dataclass
class VideoNotesCollected(Event):
    """Event: User has provided notes for a video"""
    event_type: str = "video.notes_collected"
    video_url: str = ""
    video_title: str = ""
    notes: str = ""
    topic: str = ""
    date_collected: str = ""


# Helper functions for creating common video events

def create_video_search_request(topic: str, parent_topic: str = "",
                               feedback_history: Dict[str, Any] = None,
                               session_id: str = None, user_id: str = None) -> VideoSearchRequested:
    """Create a video search request event"""
    return VideoSearchRequested(
        topic=topic,
        parent_topic=parent_topic,
        feedback_history=feedback_history or {},
        session_id=session_id,
        user_id=user_id
    )


def create_video_recommendation_request(available_videos: List[Dict[str, Any]],
                                      topic: str, parent_topic: str = "",
                                      feedback_history: Dict[str, Any] = None,
                                      session_id: str = None, user_id: str = None) -> VideoRecommendationRequested:
    """Create a video recommendation request event"""
    return VideoRecommendationRequested(
        available_videos=available_videos,
        topic=topic,
        parent_topic=parent_topic,
        feedback_history=feedback_history or {},
        session_id=session_id,
        user_id=user_id
    )


def create_video_recommended_event(video_data: Dict[str, Any], blurb: str,
                                 topic: str, parent_topic: str = "",
                                 session_id: str = None, user_id: str = None) -> VideoRecommended:
    """Create a video recommended event from video data and recommendation"""
    return VideoRecommended(
        video_id=video_data.get("video_id", ""),
        video_title=video_data.get("title", ""),
        channel_title=video_data.get("channel_title", ""),
        video_url=video_data.get("video_url", ""),
        thumbnail_url=video_data.get("thumbnail_url", ""),
        blurb=blurb,
        topic=topic,
        parent_topic=parent_topic,
        session_id=session_id,
        user_id=user_id
    )