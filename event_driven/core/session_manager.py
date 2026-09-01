"""
Session Manager for YouTube Hobby Maxxxer Event-Driven Architecture

Manages user sessions, state persistence, and context across event flows.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid


class SessionState(Enum):
    """Session states for tracking user interaction flows"""
    IDLE = "idle"
    AWAITING_FEEDBACK = "awaiting_feedback"
    AWAITING_NOTES = "awaiting_notes"
    AWAITING_TOPIC_SELECTION = "awaiting_topic_selection"
    AWAITING_INTEREST_CONFIRMATION = "awaiting_interest_confirmation"
    PROCESSING = "processing"
    COMPLETED = "completed"
    EXPIRED = "expired"


@dataclass
class UserSession:
    """User session data container"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    discord_user_id: int = 0
    username: str = ""

    # Session metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    state: SessionState = SessionState.IDLE
    session_type: str = "interactive"  # interactive, daily_job, topic_exploration

    # Current workflow context
    current_workflow: str = ""
    workflow_step: str = ""
    workflow_data: Dict[str, Any] = field(default_factory=dict)

    # Conversation state
    awaiting_response_for: Optional[int] = None  # Discord message ID
    conversation_context: Dict[str, Any] = field(default_factory=dict)

    # User preferences and history (cached)
    feedback_history: Dict[str, Any] = field(default_factory=dict)
    topic_interests: Dict[str, float] = field(default_factory=dict)
    recent_videos: List[Dict[str, Any]] = field(default_factory=list)

    # Interaction statistics
    interactions_count: int = 0
    videos_recommended: int = 0
    feedback_given: int = 0
    notes_provided: int = 0

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.interactions_count += 1

    def set_state(self, new_state: SessionState, workflow_data: Dict[str, Any] = None):
        """Update session state and optional workflow data"""
        self.state = new_state
        self.update_activity()
        if workflow_data:
            self.workflow_data.update(workflow_data)

    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if session has expired based on last activity"""
        cutoff = datetime.now() - timedelta(hours=timeout_hours)
        return self.last_activity < cutoff

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization"""
        data = asdict(self)
        # Convert datetime objects to strings
        data['created_at'] = self.created_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        data['state'] = self.state.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create session from dictionary"""
        # Convert datetime strings back to datetime objects
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'last_activity' in data:
            data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        if 'state' in data:
            data['state'] = SessionState(data['state'])

        return cls(**data)


class SessionManager:
    """
    Manages user sessions for the event-driven system.

    Provides session lifecycle management, state persistence,
    and context tracking across event flows.
    """

    def __init__(self, cleanup_interval_minutes: int = 30, session_timeout_hours: int = 24):
        self.sessions: Dict[str, UserSession] = {}  # session_id -> UserSession
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.cleanup_interval = cleanup_interval_minutes
        self.session_timeout = session_timeout_hours
        self._cleanup_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Statistics
        self.stats = {
            'sessions_created': 0,
            'sessions_expired': 0,
            'total_interactions': 0,
            'cleanup_runs': 0
        }

    async def start(self):
        """Start the session manager and cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_worker())
            self.logger.info("🔄 Session manager started")

    async def stop(self):
        """Stop the session manager and cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            self.logger.info("🛑 Session manager stopped")

    async def create_session(self, user_id: str, discord_user_id: int,
                           username: str = "", session_type: str = "interactive") -> UserSession:
        """Create a new user session"""
        # End any existing session for this user
        await self.end_user_session(user_id)

        session = UserSession(
            user_id=user_id,
            discord_user_id=discord_user_id,
            username=username,
            session_type=session_type
        )

        self.sessions[session.session_id] = session
        self.user_sessions[user_id] = session.session_id
        self.stats['sessions_created'] += 1

        self.logger.info(f"📝 Created session {session.session_id[:8]} for user {username}")
        return session

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by session ID"""
        session = self.sessions.get(session_id)
        if session and session.is_expired(self.session_timeout):
            await self.end_session(session_id, reason="expired")
            return None
        return session

    async def get_user_session(self, user_id: str) -> Optional[UserSession]:
        """Get active session for a user"""
        session_id = self.user_sessions.get(user_id)
        if session_id:
            return await self.get_session(session_id)
        return None

    async def get_or_create_session(self, user_id: str, discord_user_id: int,
                                   username: str = "", session_type: str = "interactive") -> UserSession:
        """Get existing session or create new one"""
        session = await self.get_user_session(user_id)
        if session is None:
            session = await self.create_session(user_id, discord_user_id, username, session_type)
        return session

    async def update_session_state(self, session_id: str, new_state: SessionState,
                                 workflow_data: Dict[str, Any] = None) -> bool:
        """Update session state"""
        session = await self.get_session(session_id)
        if session:
            old_state = session.state
            session.set_state(new_state, workflow_data)
            self.logger.debug(f"🔄 Session {session_id[:8]} state: {old_state.value} → {new_state.value}")
            return True
        return False

    async def update_session_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """Update session conversation context"""
        session = await self.get_session(session_id)
        if session:
            session.conversation_context.update(context_updates)
            session.update_activity()
            self.stats['total_interactions'] += 1
            return True
        return False

    async def record_interaction(self, session_id: str, interaction_type: str,
                               interaction_data: Dict[str, Any] = None) -> bool:
        """Record user interaction in session"""
        session = await self.get_session(session_id)
        if session:
            session.update_activity()

            # Update specific counters
            if interaction_type == "video_recommended":
                session.videos_recommended += 1
            elif interaction_type == "feedback_given":
                session.feedback_given += 1
            elif interaction_type == "notes_provided":
                session.notes_provided += 1

            # Store interaction data in context
            if interaction_data:
                if 'interactions' not in session.conversation_context:
                    session.conversation_context['interactions'] = []
                session.conversation_context['interactions'].append({
                    'type': interaction_type,
                    'timestamp': datetime.now().isoformat(),
                    'data': interaction_data
                })

            self.logger.debug(f"📊 Recorded interaction '{interaction_type}' for session {session_id[:8]}")
            return True
        return False

    async def end_session(self, session_id: str, reason: str = "normal") -> bool:
        """End a specific session"""
        session = self.sessions.get(session_id)
        if session:
            # Remove from active sessions
            del self.sessions[session_id]
            if session.user_id in self.user_sessions:
                del self.user_sessions[session.user_id]

            duration = (datetime.now() - session.created_at).total_seconds() / 60
            self.logger.info(f"⏹️  Ended session {session_id[:8]} for {session.username} "
                           f"({duration:.1f}m, {session.interactions_count} interactions, reason: {reason})")
            return True
        return False

    async def end_user_session(self, user_id: str, reason: str = "normal") -> bool:
        """End active session for a user"""
        session_id = self.user_sessions.get(user_id)
        if session_id:
            return await self.end_session(session_id, reason)
        return False

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if session.is_expired(self.session_timeout):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            await self.end_session(session_id, reason="expired")
            self.stats['sessions_expired'] += 1

        if expired_sessions:
            self.logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    async def _cleanup_worker(self):
        """Background worker for session cleanup"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval * 60)  # Convert to seconds
                await self.cleanup_expired_sessions()
                self.stats['cleanup_runs'] += 1
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Session cleanup error: {e}")

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active sessions with basic info"""
        active_sessions = []
        for session in self.sessions.values():
            if not session.is_expired(self.session_timeout):
                active_sessions.append({
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'username': session.username,
                    'state': session.state.value,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'interactions': session.interactions_count
                })
        return active_sessions

    def get_stats(self) -> Dict[str, Any]:
        """Get session manager statistics"""
        return {
            **self.stats,
            'active_sessions': len(self.sessions),
            'user_mappings': len(self.user_sessions),
            'average_session_interactions': (
                sum(s.interactions_count for s in self.sessions.values()) / len(self.sessions)
                if self.sessions else 0
            )
        }

    async def export_sessions(self, include_context: bool = False) -> Dict[str, Any]:
        """Export sessions for backup or analysis"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'sessions': []
        }

        for session in self.sessions.values():
            session_data = session.to_dict()
            if not include_context:
                # Remove large context data for smaller exports
                session_data.pop('conversation_context', None)
                session_data.pop('workflow_data', None)
            export_data['sessions'].append(session_data)

        return export_data

    async def import_sessions(self, import_data: Dict[str, Any]) -> int:
        """Import sessions from backup data"""
        imported_count = 0

        for session_data in import_data.get('sessions', []):
            try:
                session = UserSession.from_dict(session_data)
                if not session.is_expired(self.session_timeout):
                    self.sessions[session.session_id] = session
                    self.user_sessions[session.user_id] = session.session_id
                    imported_count += 1
            except Exception as e:
                self.logger.error(f"❌ Failed to import session: {e}")

        if imported_count > 0:
            self.logger.info(f"📥 Imported {imported_count} sessions")

        return imported_count


# Global session manager instance
_global_session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _global_session_manager
    if _global_session_manager is None:
        _global_session_manager = SessionManager()
    return _global_session_manager