"""
Event Bus - Core event-driven messaging system for YouTube Hobby Maxxxer

This lightweight asyncio-based event system provides pub/sub functionality
without external dependencies like Redis or RabbitMQ.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid
import traceback


@dataclass
class Event:
    """Base event class with correlation tracking"""
    event_id: str = None
    event_type: str = ""
    timestamp: datetime = None
    correlation_id: str = None
    session_id: str = None
    user_id: str = None
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.data is None:
            self.data = {}


class EventBus:
    """
    Lightweight async event bus for decoupled component communication.

    Features:
    - Async event handling with error isolation
    - Wildcard event subscriptions (e.g., "video.*")
    - Event correlation for debugging and tracing
    - Built-in error handling and retry logic
    - No external dependencies
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._event_queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Statistics for monitoring
        self.stats = {
            'events_published': 0,
            'events_processed': 0,
            'errors': 0,
            'handlers_executed': 0
        }

    async def start(self):
        """Start the event bus worker"""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._event_worker())
        self.logger.info("🚀 Event bus started")

    async def stop(self):
        """Stop the event bus gracefully"""
        if not self._running:
            return

        self._running = False

        # Stop accepting new events
        await self._event_queue.put(None)  # Sentinel to stop worker

        # Wait for worker to finish
        if self._worker_task:
            await self._worker_task

        self.logger.info("🛑 Event bus stopped")

    def subscribe(self, event_pattern: str, handler: Callable):
        """
        Subscribe a handler to events matching the pattern.

        Args:
            event_pattern: Event type pattern (e.g., "video.recommended", "video.*")
            handler: Async function to handle the event
        """
        if event_pattern not in self._handlers:
            self._handlers[event_pattern] = []

        self._handlers[event_pattern].append(handler)
        self.logger.debug(f"📝 Subscribed handler to {event_pattern}")

    def unsubscribe(self, event_pattern: str, handler: Callable):
        """Remove a handler subscription"""
        if event_pattern in self._handlers:
            try:
                self._handlers[event_pattern].remove(handler)
                if not self._handlers[event_pattern]:
                    del self._handlers[event_pattern]
                self.logger.debug(f"❌ Unsubscribed handler from {event_pattern}")
            except ValueError:
                pass

    async def publish(self, event: Event):
        """
        Publish an event to the bus.

        Args:
            event: Event instance to publish
        """
        if not self._running:
            await self.start()

        self.stats['events_published'] += 1
        await self._event_queue.put(event)

        self.logger.debug(f"📤 Published event: {event.event_type} (ID: {event.event_id})")

    async def publish_and_wait(self, event: Event, timeout: float = 5.0):
        """
        Publish an event and wait for all handlers to complete.

        Useful for synchronous-like behavior when needed.
        """
        completion_event = asyncio.Event()
        event.data['_completion_event'] = completion_event

        await self.publish(event)

        try:
            await asyncio.wait_for(completion_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"⏰ Timeout waiting for event handlers: {event.event_type}")

    async def _event_worker(self):
        """Background worker that processes events from the queue"""
        while self._running:
            try:
                # Wait for events
                event = await self._event_queue.get()

                # Sentinel value to stop worker
                if event is None:
                    break

                await self._process_event(event)
                self.stats['events_processed'] += 1

            except Exception as e:
                self.logger.error(f"❌ Event worker error: {e}")
                self.stats['errors'] += 1

    async def _process_event(self, event: Event):
        """Process a single event by calling all matching handlers"""
        matching_handlers = self._find_handlers(event.event_type)

        if not matching_handlers:
            self.logger.debug(f"📪 No handlers for event: {event.event_type}")
            return

        # Execute all handlers concurrently
        tasks = []
        for handler in matching_handlers:
            task = asyncio.create_task(self._execute_handler(handler, event))
            tasks.append(task)

        # Wait for all handlers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for completion event signaling
        completion_event = event.data.get('_completion_event')
        if completion_event:
            completion_event.set()

        # Log any handler errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Handler error for {event.event_type}: {result}")
                self.stats['errors'] += 1

    async def _execute_handler(self, handler: Callable, event: Event):
        """Execute a single event handler with error isolation"""
        try:
            self.stats['handlers_executed'] += 1

            # Support both sync and async handlers
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)

            self.logger.debug(f"✅ Handler executed for {event.event_type}")

        except Exception as e:
            # Log error but don't let it crash other handlers
            self.logger.error(f"❌ Handler failed for {event.event_type}: {e}")
            self.logger.debug(f"Handler traceback: {traceback.format_exc()}")
            raise  # Re-raise for gather() to catch

    def _find_handlers(self, event_type: str) -> List[Callable]:
        """Find all handlers that match the event type, including wildcards"""
        matching_handlers = []

        for pattern, handlers in self._handlers.items():
            if self._match_pattern(pattern, event_type):
                matching_handlers.extend(handlers)

        return matching_handlers

    def _match_pattern(self, pattern: str, event_type: str) -> bool:
        """Check if an event type matches a subscription pattern"""
        # Exact match
        if pattern == event_type:
            return True

        # Wildcard match (e.g., "video.*" matches "video.recommended")
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return event_type.startswith(prefix)

        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics for monitoring"""
        return {
            **self.stats,
            'active_patterns': len(self._handlers),
            'total_handlers': sum(len(handlers) for handlers in self._handlers.values()),
            'queue_size': self._event_queue.qsize(),
            'running': self._running
        }


# Convenience function for creating typed events
def create_event(event_type: str, data: Dict[str, Any] = None, **kwargs) -> Event:
    """Create an event with the specified type and data"""
    return Event(
        event_type=event_type,
        data=data or {},
        **kwargs
    )


# Global event bus instance (singleton pattern)
_global_bus = None

def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus