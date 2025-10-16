#!/usr/bin/env python3
"""
Explore device capabilities and additional data available.

Looking for:
- Per-outlet current draw
- Voltage information
- Power (watts)
- Uptime
- Firmware version
- Serial number
- Additional status fields
- Historical data
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = os.getenv("NETCOMMANDER_USER", "admin")
PASSWORD = os.getenv("NETCOMMANDER_PASSWORD", "admin")


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


async def test_command(session: aiohttp.ClientSession, cmd: str, description: str) -> tuple:
    """Test a command and return response."""
    url = f"http://{HOST}/cmd.cgi?{cmd}"
    try:
        async with session.get(url) as resp:
            text = (await resp.text()).strip()
            return (resp.status, text)
    except Exception as e:
        return (0, str(e))


async def fetch_webpage(session: aiohttp.ClientSession, path: str) -> str:
    """Fetch a webpage and return content."""
    url = f"http://{HOST}{path}"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            return f"HTTP {resp.status}"
    except Exception as e:
        return str(e)


async def main():
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print(" Device Capabilities Discovery ".center(80))
    print("="*80)
    print(Colors.END)

    auth = aiohttp.BasicAuth(USER, PASSWORD)

    async with aiohttp.ClientSession(auth=auth) as session:
        # Test 1: Status command variants
        print(f"\n{Colors.BOLD}Test 1: Status Command Variations{Colors.END}")
        print("-"*80)

        status_commands = [
            ("$A5", "Standard status"),
            ("$A6", "Extended status (guess)"),
            ("status", "Status keyword"),
            ("info", "Info keyword"),
            ("ver", "Version"),
            ("version", "Version alt"),
        ]

        for cmd, desc in status_commands:
            status, response = await test_command(session, cmd, desc)
            if status == 200 and not response.startswith("$AF"):
                print(f"{Colors.GREEN}✓{Colors.END} {desc:20} → {response[:80]}")
            else:
                print(f"{Colors.RED}✗{Colors.END} {desc:20} → {response[:50]}")

        # Test 2: Per-outlet current
        print(f"\n{Colors.BOLD}Test 2: Per-Outlet Current Draw{Colors.END}")
        print("-"*80)
        print("Testing if device reports individual outlet current...")

        # Turn on outlets one by one and check current
        print("\nBaseline (all off):")
        status, response = await test_command(session, "$A5", "")
        print(f"  Response: {response}")
        parts = response.split(",")
        if len(parts) >= 3:
            print(f"  Total current: {parts[2]}A")
            baseline_current = float(parts[2])

        # Turn on outlet 1
        await test_command(session, "$A3 1 1", "Turn on outlet 1")
        await asyncio.sleep(1)

        status, response = await test_command(session, "$A5", "")
        print(f"\nOutlet 1 ON:")
        print(f"  Response: {response}")
        parts = response.split(",")

        # Check if response has more fields
        print(f"  Response parts: {len(parts)}")
        for i, part in enumerate(parts):
            print(f"    [{i}]: {part}")

        # Look for per-outlet current in response
        if len(parts) > 4:
            print(f"\n{Colors.GREEN}✓ Additional data fields found!{Colors.END}")
            for i in range(4, len(parts)):
                print(f"    Extra field [{i}]: {parts[i]}")

        # Turn off outlet 1
        await test_command(session, "$A3 1 0", "Turn off outlet 1")
        await asyncio.sleep(1)

        # Test 3: Check documentation mentions
        print(f"\n{Colors.BOLD}Test 3: Check for Advanced Commands{Colors.END}")
        print("-"*80)

        advanced_commands = [
            ("$A8", "Unknown A8"),
            ("$A9", "Unknown A9"),
            ("$AA", "Unknown AA"),
            ("current", "Current keyword"),
            ("power", "Power keyword"),
            ("voltage", "Voltage keyword"),
            ("uptime", "Uptime"),
            ("sysinfo", "System info"),
        ]

        for cmd, desc in advanced_commands:
            status, response = await test_command(session, cmd, desc)
            if status == 200 and response and not response.startswith("$AF"):
                print(f"{Colors.GREEN}✓{Colors.END} {desc:20} → {response[:60]}")

        # Test 4: Web interface scraping
        print(f"\n{Colors.BOLD}Test 4: Web Interface Data{Colors.END}")
        print("-"*80)
        print("Checking web interface for additional device info...")

        web_pages = [
            ("/", "Main page"),
            ("/index.html", "Index page"),
            ("/status.html", "Status page"),
            ("/info.html", "Info page"),
            ("/system.html", "System page"),
        ]

        for path, desc in web_pages:
            content = await fetch_webpage(session, path)
            if content and "HTTP" not in content[:10]:
                print(f"{Colors.GREEN}✓{Colors.END} {desc:20} → {len(content)} bytes")

                # Look for useful info in HTML
                keywords = ["firmware", "version", "serial", "model", "voltage", "current", "power", "uptime"]
                found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
                if found_keywords:
                    print(f"    Keywords found: {', '.join(found_keywords)}")
            else:
                print(f"{Colors.RED}✗{Colors.END} {desc:20} → Not found")

        # Test 5: Detailed status string analysis
        print(f"\n{Colors.BOLD}Test 5: Detailed Status String Analysis{Colors.END}")
        print("-"*80)

        # Turn on all outlets to get max current reading
        print("Turning on all outlets to test current measurement...")
        for i in range(1, 6):
            await test_command(session, f"$A3 {i} 1", f"Turn on {i}")
            await asyncio.sleep(0.5)

        status, response = await test_command(session, "$A5", "")
        print(f"\nAll outlets ON:")
        print(f"  Raw response: {repr(response)}")

        parts = response.split(",")
        print(f"  Total parts: {len(parts)}")
        for i, part in enumerate(parts):
            print(f"    Part {i}: '{part}' ({len(part)} chars)")

        # Turn all off
        for i in range(1, 6):
            await test_command(session, f"$A3 {i} 0", f"Turn off {i}")

        # Test 6: Check SNMP/MIB capabilities
        print(f"\n{Colors.BOLD}Test 6: Additional Protocol Support{Colors.END}")
        print("-"*80)
        print("Note: Device supports SNMP (community: 'public' by default)")
        print("      This could provide additional metrics via SNMP queries")
        print("      MIB file available at: Network Settings → 'get mib file'")

        # Summary
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("="*80)
        print(" Summary ".center(80))
        print("="*80)
        print(Colors.END)

        print(f"\n{Colors.BOLD}Currently Available Data:{Colors.END}")
        print("  • Per-outlet state (ON/OFF)")
        print("  • Total current draw (Amps)")
        print("  • Temperature (if available)")
        print("  • Device response code")

        print(f"\n{Colors.BOLD}Potentially Available (need testing):{Colors.END}")
        print("  • Per-outlet current (if in extended status)")
        print("  • Voltage information")
        print("  • Power consumption (watts)")
        print("  • Uptime")
        print("  • Firmware version")
        print("  • Model/Serial number")

        print(f"\n{Colors.BOLD}Additional Data Sources:{Colors.END}")
        print("  • SNMP queries (via MIB file)")
        print("  • Web interface scraping")
        print("  • Device configuration page")

        print(f"\n{Colors.YELLOW}Recommendation:{Colors.END}")
        print("  1. Check if SNMP provides per-outlet current")
        print("  2. Scrape web interface for device info (firmware, model, etc.)")
        print("  3. Check device admin panel for advanced metrics")

    return 0


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}")
        sys.exit(130)
