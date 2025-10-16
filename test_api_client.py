#!/usr/bin/env python3
"""
Test the new API client library.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path so we can import netcommander
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from netcommander import NetCommanderClient, DeviceStatus

load_dotenv()

HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = os.getenv("NETCOMMANDER_USER", "admin")
PASSWORD = os.getenv("NETCOMMANDER_PASSWORD", "admin")


async def main():
    print("="*80)
    print(" Testing NetCommander API Client ".center(80))
    print("="*80)
    print()

    async with NetCommanderClient(HOST, USER, PASSWORD) as client:
        # Test 1: Get status
        print("Test 1: Get Status")
        print("-" * 40)
        status = await client.get_status()

        print(f"Total Current: {status.total_current_amps}A")
        print(f"Temperature: {status.temperature}")
        print(f"\nOutlets:")
        for outlet_num in range(1, 6):
            state = "ON " if status.outlets[outlet_num] else "OFF"
            print(f"  Outlet {outlet_num}: {state}")

        print(f"\nOutlets ON: {status.outlets_on}")
        print(f"Outlets OFF: {status.outlets_off}")
        print(f"All ON: {status.all_on}")
        print(f"All OFF: {status.all_off}")

        # Test 2: Turn on outlet 1
        print("\n\nTest 2: Turn ON Outlet 1")
        print("-" * 40)
        success = await client.turn_on(1)
        print(f"Command success: {success}")

        # Verify
        state = await client.get_outlet_state(1)
        print(f"Outlet 1 is now: {'ON' if state else 'OFF'}")

        # Test 3: Turn off outlet 1
        print("\n\nTest 3: Turn OFF Outlet 1")
        print("-" * 40)
        success = await client.turn_off(1)
        print(f"Command success: {success}")

        # Verify
        state = await client.get_outlet_state(1)
        print(f"Outlet 1 is now: {'ON' if state else 'OFF'}")

        # Test 4: Turn all ON
        print("\n\nTest 4: Turn All ON")
        print("-" * 40)
        results = await client.turn_on_all()
        for outlet, success in results.items():
            print(f"  Outlet {outlet}: {'✓' if success else '✗'}")

        status = await client.get_status()
        print(f"All ON: {status.all_on}")

        # Test 5: Turn all OFF
        print("\n\nTest 5: Turn All OFF")
        print("-" * 40)
        results = await client.turn_off_all()
        for outlet, success in results.items():
            print(f"  Outlet {outlet}: {'✓' if success else '✗'}")

        status = await client.get_status()
        print(f"All OFF: {status.all_off}")

    print("\n" + "="*80)
    print(" All Tests Complete ".center(80))
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
