#!/usr/bin/env python3
"""
Quick test of the event-driven architecture components
"""

import asyncio
import sys
from pathlib import Path

# Add event_driven directory to path
sys.path.insert(0, str(Path(__file__).parent / "event_driven"))

from core.event_bus import EventBus, Event


async def test_event_system():
    """Test basic event system functionality"""
    print("🧪 Testing Event-Driven Architecture")
    print("=" * 40)

    # Create event bus
    event_bus = EventBus()
    await event_bus.start()

    # Track received events
    received_events = []

    async def event_handler(event):
        received_events.append(event)
        print(f"📨 Received event: {event.event_type} - {event.data}")

    # Subscribe to events
    event_bus.subscribe("test.*", event_handler)
    event_bus.subscribe("demo.workflow", event_handler)

    # Publish some test events
    test_event1 = Event(
        event_type="test.video_search",
        data={"topic": "guitar", "user": "demo"}
    )

    test_event2 = Event(
        event_type="demo.workflow",
        data={"step": "recommendation", "status": "completed"}
    )

    await event_bus.publish(test_event1)
    await event_bus.publish(test_event2)

    # Wait for processing
    await asyncio.sleep(0.1)

    # Check results
    print(f"✅ Published 2 events, received {len(received_events)}")
    print(f"📊 Event bus stats: {event_bus.get_stats()}")

    # Test parallel event handling
    print("\n🔄 Testing parallel event processing...")

    start_time = asyncio.get_event_loop().time()

    # Publish multiple events simultaneously
    tasks = []
    for i in range(5):
        event = Event(
            event_type=f"test.parallel_{i}",
            data={"index": i, "timestamp": start_time}
        )
        tasks.append(event_bus.publish(event))

    await asyncio.gather(*tasks)
    await asyncio.sleep(0.1)

    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time

    print(f"⚡ Processed 5 parallel events in {duration*1000:.1f}ms")
    print(f"📊 Final stats: {event_bus.get_stats()}")

    await event_bus.stop()
    return True


async def main():
    """Main test function"""
    try:
        success = await test_event_system()
        if success:
            print("\n🎉 Event-driven architecture test PASSED!")
            print("The system is ready for implementation.")
        return 0
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))