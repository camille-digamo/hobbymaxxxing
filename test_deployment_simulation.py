#!/usr/bin/env python3
"""
Deployment Simulation Test
=========================
Simulates GitHub Actions + Railway deployment locally.
"""

import asyncio
import subprocess
import time
import sys
import os

def run_in_background(command):
    """Run command in background and return process"""
    return subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

async def simulate_deployment():
    """Simulate the GitHub Actions + Railway deployment"""
    print("🎯 Simulating GitHub Actions + Railway Deployment")
    print("=" * 50)

    print("\n🚂 Starting Railway simulation (--listen mode)...")
    listener_process = run_in_background("python3 main.py --listen")

    # Give listener time to start up
    print("⏳ Waiting for listener to start up...")
    await asyncio.sleep(5)

    print("✅ Railway listener is running in background")

    # Check if listener started successfully
    if listener_process.poll() is not None:
        print("❌ Listener process failed to start!")
        stdout, stderr = listener_process.communicate()
        print(f"Error: {stderr}")
        return False

    print("\n🐙 Triggering GitHub Actions simulation (--daily-job)...")
    daily_job_result = subprocess.run(
        ["python3", "main.py", "--daily-job"],
        capture_output=True,
        text=True,
        timeout=60
    )

    if daily_job_result.returncode == 0:
        print("✅ Daily job completed successfully!")
        print("📤 Video should be posted to Discord with reaction buttons")
    else:
        print(f"❌ Daily job failed: {daily_job_result.stderr}")
        listener_process.terminate()
        return False

    print("\n👆 Now react to the video in Discord and watch the listener logs...")
    print("🔍 Listener process is running - check your terminal for reaction detection")
    print("📊 Check Google Sheets to see if feedback is recorded")
    print("\n⏹️  Press Enter when you want to stop the simulation...")

    # Wait for user input
    input()

    print("\n🛑 Stopping Railway simulation...")
    listener_process.terminate()

    # Wait a bit for graceful shutdown
    try:
        listener_process.wait(timeout=5)
        print("✅ Listener stopped gracefully")
    except subprocess.TimeoutExpired:
        listener_process.kill()
        print("🔪 Listener process killed")

    print("\n🎉 Deployment simulation complete!")
    return True

def main():
    """Main simulation function"""
    try:
        result = asyncio.run(simulate_deployment())
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())