#!/usr/bin/env python3
"""Test the new device info API."""

import asyncio
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from netcommander import NetCommanderClient

load_dotenv()

HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = os.getenv("NETCOMMANDER_USER", "admin")
PASSWORD = os.getenv("NETCOMMANDER_PASSWORD", "admin")


async def main():
    print("Testing Device Info API")
    print("="*60)

    async with NetCommanderClient(HOST, USER, PASSWORD) as client:
        device_info = await client.get_device_info()

        print(f"\nModel: {device_info.model}")
        print(f"Hardware Version: {device_info.hardware_version}")
        print(f"Firmware Version: {device_info.firmware_version}")
        print(f"Bootloader Version: {device_info.bootloader_version}")
        print(f"MAC Address: {device_info.mac_address}")
        print(f"\nRaw Response: {device_info.raw_response}")

    print("\n" + "="*60)
    print("✓ API Test Complete")


if __name__ == "__main__":
    asyncio.run(main())
