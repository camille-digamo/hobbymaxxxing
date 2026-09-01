"""
Topic-related events for the YouTube Hobby Maxxxer.

These events handle topic selection, expansion, and interest detection.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.event_bus import Event


@dataclass
class TopicSelectionRequested(Event):
    """Event: Request to select next topic using smart algorithm"""
    event_type: str = "topic.selection_requested"
    selection_method: str = "smart"  # smart, random, specific
    specific_topic: str = ""
    force_topic: bool = False


@dataclass
class TopicSelected(Event):
    """Event: Topic has been selected for video recommendation"""
    event_type: str = "topic.selected"
    topic: str = ""
    parent_topic: str = ""
    topic_row: int = 0
    selection_weight: float = 0.0
    selection_method: str = ""
    candidate_count: int = 0


@dataclass
class TopicExpansionRequested(Event):
    """Event: Request topic expansion due to no available videos"""
    event_type: str = "topic.expansion_requested"
    original_topic: str = ""
    parent_topic: str = ""
    reason: str = "no_videos"  # no_videos, user_request
    discord_channel_id: int = 0


@dataclass
class TopicExpansionGenerated(Event):
    """Event: AI has generated topic expansion suggestions"""
    event_type: str = "topic.expansion_generated"
    original_topic: str = ""
    parent_topic: str = ""
    suggested_topics: List[str] = None
    suggested_parent: str = ""
    expansion_reasoning: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.suggested_topics is None:
            self.suggested_topics = []


@dataclass
class TopicExpansionPresented(Event):
    """Event: Topic expansion options presented to user"""
    event_type: str = "topic.expansion_presented"
    original_topic: str = ""
    suggested_topics: List[str] = None
    discord_message_id: int = 0
    discord_channel_id: int = 0
    awaiting_selection: bool = True

    def __post_init__(self):
        super().__post_init__()
        if self.suggested_topics is None:
            self.suggested_topics = []


@dataclass
class TopicExpansionSelected(Event):
    """Event: User has selected topics from expansion"""
    event_type: str = "topic.expansion_selected"
    selected_topics: List[str] = None
    parent_topic: str = ""
    user_response: str = ""
    selection_method: str = "numbers"  # numbers, names, custom

    def __post_init__(self):
        super().__post_init__()
        if self.selected_topics is None:
            self.selected_topics = []


@dataclass
class TopicInterestDetected(Event):
    """Event: Natural language interest detection from user message"""
    event_type: str = "topic.interest_detected"
    raw_message: str = ""
    extracted_topics: List[str] = None
    confidence_score: float = 0.0
    detection_method: str = "regex"  # regex, nlp, keyword
    discord_message_id: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.extracted_topics is None:
            self.extracted_topics = []


@dataclass
class TopicInterestAnalysisRequested(Event):
    """Event: Request AI analysis of topic interest"""
    event_type: str = "topic.interest_analysis_requested"
    raw_topic: str = ""
    existing_topics: List[str] = None
    discord_message_id: int = 0

    def __post_init__(self):
        super().__post_init__()
        if self.existing_topics is None:
            self.existing_topics = []


@dataclass
class TopicInterestAnalyzed(Event):
    """Event: AI has analyzed topic interest and provided suggestions"""
    event_type: str = "topic.interest_analyzed"
    original_topic: str = ""
    refined_topic: str = ""
    parent_topic: str = ""
    suggested_related: List[str] = None
    confidence: float = 0.0
    needs_confirmation: bool = True

    def __post_init__(self):
        super().__post_init__()
        if self.suggested_related is None:
            self.suggested_related = []


@dataclass
class TopicsAdded(Event):
    """Event: New topics successfully added to Google Sheets"""
    event_type: str = "topic.topics_added"
    added_topics: List[str] = None
    parent_topic: str = ""
    sheet_rows: List[int] = None
    date_added: str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.added_topics is None:
            self.added_topics = []
        if self.sheet_rows is None:
            self.sheet_rows = []


@dataclass
class TopicScoresCalculated(Event):
    """Event: Topic interest scores have been calculated"""
    event_type: str = "topic.scores_calculated"
    topic_scores: Dict[str, float] = None
    total_topics: int = 0
    calculation_method: str = "weighted"

    def __post_init__(self):
        super().__post_init__()
        if self.topic_scores is None:
            self.topic_scores = {}


@dataclass
class TopicHistoryUpdated(Event):
    """Event: Topic watch history has been updated"""
    event_type: str = "topic.history_updated"
    topic: str = ""
    last_watched: str = ""
    videos_watched: int = 0
    interest_score: float = 0.0


# Helper functions for creating common topic events

def create_topic_selection_request(method: str = "smart", specific_topic: str = "",
                                 session_id: str = None, user_id: str = None) -> TopicSelectionRequested:
    """Create a topic selection request event"""
    return TopicSelectionRequested(
        selection_method=method,
        specific_topic=specific_topic,
        session_id=session_id,
        user_id=user_id
    )


def create_topic_selected_event(topic: str, parent_topic: str, topic_row: int,
                               selection_weight: float = 0.0, method: str = "smart",
                               session_id: str = None, user_id: str = None) -> TopicSelected:
    """Create a topic selected event"""
    return TopicSelected(
        topic=topic,
        parent_topic=parent_topic,
        topic_row=topic_row,
        selection_weight=selection_weight,
        selection_method=method,
        session_id=session_id,
        user_id=user_id
    )


def create_topic_expansion_request(original_topic: str, parent_topic: str = "",
                                 reason: str = "no_videos", channel_id: int = 0,
                                 session_id: str = None, user_id: str = None) -> TopicExpansionRequested:
    """Create a topic expansion request event"""
    return TopicExpansionRequested(
        original_topic=original_topic,
        parent_topic=parent_topic,
        reason=reason,
        discord_channel_id=channel_id,
        session_id=session_id,
        user_id=user_id
    )


def create_topic_interest_detection(message: str, topics: List[str], confidence: float,
                                  message_id: int = 0, session_id: str = None,
                                  user_id: str = None) -> TopicInterestDetected:
    """Create a topic interest detection event"""
    return TopicInterestDetected(
        raw_message=message,
        extracted_topics=topics,
        confidence_score=confidence,
        discord_message_id=message_id,
        session_id=session_id,
        user_id=user_id
    )