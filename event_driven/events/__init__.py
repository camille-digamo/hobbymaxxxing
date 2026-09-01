"""
Event definitions for YouTube Hobby Maxxxer event-driven architecture.

This module defines all the events that flow through the system,
providing type safety and clear contracts between components.
"""

from .video_events import *
from .topic_events import *
from .discord_events import *
from .system_events import *
from .user_events import *