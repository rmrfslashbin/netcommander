#!/usr/bin/env python3
"""
Extract detailed device information from $A8 command and web interface.
"""

import asyncio
import re
from html.parser import HTMLParser
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = os.getenv("NETCOMMANDER_USER", "admin")
PASSWORD = os.getenv("NETCOMMANDER_PASSWORD", "admin")


class DeviceInfoParser(HTMLParser):
    """Parse HTML to extract device information."""

    def __init__(self):
        super().__init__()
        self.data = {}
        self.in_relevant_section = False
        self.last_tag = None
        self.last_data = None

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        # Look for key-value patterns
        if any(keyword in data.lower() for keyword in ['model', 'firmware', 'version', 'serial', 'hardware', 'mac']):
            self.last_data = data

        # Store interesting data
        if self.last_data and ':' in data:
            parts = data.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                self.data[key] = value


async def get_device_info(session):
    """Get device information from $A8 command."""
    url = f"http://{HOST}/cmd.cgi?$A8"
    async with session.get(url) as resp:
        if resp.status == 200:
            text = await resp.text()
            return text.strip()
    return None


async def get_web_info(session):
    """Scrape device info from web interface."""
    url = f"http://{HOST}/"
    async with session.get(url) as resp:
        if resp.status == 200:
            html = await resp.text()

            # Look for common patterns
            info = {}

            # Model
            model_match = re.search(r'model[:\s]+([^\s<,]+)', html, re.IGNORECASE)
            if model_match:
                info['model'] = model_match.group(1)

            # Firmware version
            fw_match = re.search(r'firmware[:\s]+([^\s<,]+)', html, re.IGNORECASE)
            if fw_match:
                info['firmware'] = fw_match.group(1)

            # Version
            ver_match = re.search(r'version[:\s]+([^\s<,]+)', html, re.IGNORECASE)
            if ver_match:
                info['version'] = ver_match.group(1)

            # MAC address
            mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', html)
            if mac_match:
                info['mac_address'] = mac_match.group(0)

            # Uptime
            uptime_match = re.search(r'uptime[:\s]+([^<\n]+)', html, re.IGNORECASE)
            if uptime_match:
                info['uptime'] = uptime_match.group(1).strip()

            # Voltage
            voltage_match = re.search(r'voltage[:\s]+([0-9.]+)\s*V', html, re.IGNORECASE)
            if voltage_match:
                info['voltage'] = voltage_match.group(1)

            return info
    return {}


def parse_a8_response(response):
    """Parse $A8 command response."""
    # Format: $A0,NP0501DU, HW4.3 BL1.6 -7.72-8.5
    if not response.startswith("$A0,"):
        return {}

    parts = response[4:].split(',')
    info = {}

    if len(parts) >= 1:
        info['model'] = parts[0].strip()

    if len(parts) >= 2:
        details = parts[1].strip()

        # Hardware version
        hw_match = re.search(r'HW\s*([0-9.]+)', details)
        if hw_match:
            info['hardware_version'] = hw_match.group(1)

        # Bootloader
        bl_match = re.search(r'BL\s*([0-9.]+)', details)
        if bl_match:
            info['bootloader_version'] = bl_match.group(1)

        # Firmware (everything after BL)
        fw_match = re.search(r'BL[0-9.]+\s+(.+)', details)
        if fw_match:
            info['firmware_version'] = fw_match.group(1).strip()

    return info


async def main():
    print("="*80)
    print(" Device Information Discovery ".center(80))
    print("="*80)
    print()

    auth = aiohttp.BasicAuth(USER, PASSWORD)

    async with aiohttp.ClientSession(auth=auth) as session:
        # Get info from $A8 command
        print("📡 Querying $A8 command...")
        a8_response = await get_device_info(session)

        if a8_response:
            print(f"   Raw: {a8_response}")
            a8_info = parse_a8_response(a8_response)

            print("\n   Parsed:")
            for key, value in a8_info.items():
                print(f"     {key:20}: {value}")

        # Get info from web interface
        print("\n🌐 Scraping web interface...")
        web_info = await get_web_info(session)

        if web_info:
            print("   Found:")
            for key, value in web_info.items():
                print(f"     {key:20}: {value}")

        # Combine all info
        print("\n" + "="*80)
        print(" Complete Device Information ".center(80))
        print("="*80)

        all_info = {**web_info, **a8_info}  # a8_info overwrites web_info

        if all_info:
            for key, value in sorted(all_info.items()):
                print(f"  {key:25}: {value}")
        else:
            print("  No additional information found")

        print("\n" + "="*80)
        print(" Recommendations for CLI/HA ".center(80))
        print("="*80)

        print("\n📊 Data to include in 'info' command:")
        print("  ✓ Model number")
        print("  ✓ Hardware version")
        print("  ✓ Firmware version")
        print("  ✓ Bootloader version")
        if 'mac_address' in all_info:
            print("  ✓ MAC address")
        if 'uptime' in all_info:
            print("  ✓ Device uptime")
        if 'voltage' in all_info:
            print("  ✓ Input voltage")

        print("\n📈 Additional metrics for HA:")
        print("  • Device info sensor (diagnostic)")
        print("  • Firmware version sensor (diagnostic)")
        print("  • Uptime sensor")
        if 'voltage' in all_info:
            print("  • Voltage sensor")

        print("\n💡 Note:")
        print("  • Per-outlet current NOT available (only total current)")
        print("  • Temperature sensor reports 'XX' (may not be functional)")
        print("  • SNMP might provide additional metrics (check MIB file)")


if __name__ == "__main__":
    asyncio.run(main())
