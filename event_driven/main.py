#!/usr/bin/env python3
"""
Event-Driven YouTube Hobby Maxxxer
==================================
A refactored version of the monolithic bot using event-driven architecture.

Usage:
    python event_driven/main.py --daily-job
    python event_driven/main.py --listen
    python event_driven/main.py --demo
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Event-driven imports
from core.event_bus import EventBus, get_event_bus
from core.session_manager import SessionManager, get_session_manager, SessionState
from events import *


class EventDrivenHobbyBot:
    """Event-driven version of the Hobby Maxxxer bot"""

    def __init__(self):
        self.event_bus = get_event_bus()
        self.session_manager = get_session_manager()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def start(self):
        """Start the event-driven system"""
        await self.event_bus.start()
        await self.session_manager.start()

        # Subscribe to key events for demonstration
        self.event_bus.subscribe("system.*", self.handle_system_events)
        self.event_bus.subscribe("user.session_started", self.handle_session_start)
        self.event_bus.subscribe("video.search_requested", self.handle_video_search)

        self.logger.info("🚀 Event-driven Hobby Bot started")

    async def stop(self):
        """Stop the event-driven system"""
        await self.session_manager.stop()
        await self.event_bus.stop()
        self.logger.info("🛑 Event-driven Hobby Bot stopped")

    async def handle_system_events(self, event):
        """Handle system-level events"""
        self.logger.info(f"🎯 System event: {event.event_type}")

    async def handle_session_start(self, event):
        """Handle user session start"""
        self.logger.info(f"👋 User session started: {event.username}")

        # Simulate workflow by publishing follow-up events
        await self.event_bus.publish(create_topic_selection_request(
            method="smart",
            session_id=event.session_id,
            user_id=event.user_id
        ))

    async def handle_video_search(self, event):
        """Handle video search request"""
        self.logger.info(f"🔍 Video search requested for topic: {event.topic}")

        # Simulate search completion
        await asyncio.sleep(0.1)  # Simulate API delay
        await self.event_bus.publish(VideoSearchCompleted(
            topic=event.topic,
            videos=[{"title": f"Demo video about {event.topic}", "video_id": "demo123"}],
            total_found=1,
            session_id=event.session_id,
            user_id=event.user_id
        ))


async def run_demo():
    """Run demonstration of event-driven architecture"""
    print("🎯 Event-Driven Architecture Demo")
    print("=" * 40)

    bot = EventDrivenHobbyBot()
    await bot.start()

    try:
        # Create a demo user session
        session = await bot.session_manager.create_session(
            user_id="demo_user",
            discord_user_id=12345,
            username="DemoUser",
            session_type="demo"
        )

        print(f"📝 Created session: {session.session_id[:8]}")

        # Publish demo events
        await bot.event_bus.publish(UserSessionStarted(
            user_discord_id=12345,
            username="DemoUser",
            session_type="demo",
            session_id=session.session_id,
            user_id=session.user_id
        ))

        # Wait for events to process
        await asyncio.sleep(1)

        # Show statistics
        print(f"📊 Event bus stats: {bot.event_bus.get_stats()}")
        print(f"📊 Session stats: {bot.session_manager.get_stats()}")

        # Simulate video search
        await bot.event_bus.publish(VideoSearchRequested(
            topic="guitar techniques",
            session_id=session.session_id,
            user_id=session.user_id
        ))

        await asyncio.sleep(1)
        print("✅ Demo completed successfully!")

    finally:
        await bot.stop()


async def run_daily_job():
    """Run daily job mode using event-driven architecture"""
    bot = EventDrivenHobbyBot()
    await bot.start()

    try:
        # Trigger daily job workflow
        await bot.event_bus.publish(DailyJobTriggered(
            trigger_source="manual"
        ))

        # Wait for workflow to complete
        await asyncio.sleep(2)
        print("✅ Daily job completed")

    finally:
        await bot.stop()


async def run_listener():
    """Run persistent listener mode"""
    bot = EventDrivenHobbyBot()
    await bot.start()

    try:
        # Start listener mode
        await bot.event_bus.publish(ListenerModeStarted(
            listener_type="full"
        ))

        print("👂 Listener mode started. Press Ctrl+C to stop...")

        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Stopping listener...")
    finally:
        await bot.stop()


def main():
    """Main entry point"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Parse arguments
    parser = argparse.ArgumentParser(description="Event-Driven YouTube Hobby Maxxxer")
    parser.add_argument("--daily-job", action="store_true",
                       help="Run daily video recommendation job")
    parser.add_argument("--listen", action="store_true",
                       help="Run persistent listener mode")
    parser.add_argument("--demo", action="store_true",
                       help="Run architecture demonstration")

    args = parser.parse_args()

    try:
        if args.daily_job:
            asyncio.run(run_daily_job())
        elif args.listen:
            asyncio.run(run_listener())
        elif args.demo:
            asyncio.run(run_demo())
        else:
            print("🎯 Event-Driven YouTube Hobby Maxxxer")
            print("Usage: python event_driven/main.py [--daily-job|--listen|--demo]")
            print("Run --demo to see the event architecture in action!")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())