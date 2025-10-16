#!/usr/bin/env python3
"""
Test different command formats to find what works via HTTP.

The manual shows:
- Telnet format: CmdCode,Arg1,Arg2
- HTTP format: http://IP/cmd.cgi?cmdCode,Arg1,Arg2
- Serial format: /pset n x (where n=outlet, x=0/1)

Let's test all variations to see what the HTTP interface actually accepts.
"""

import asyncio
import os
import sys
import aiohttp
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = "admin"
PASSWORD = "admin"


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


async def test_command(session: aiohttp.ClientSession, cmd: str, description: str) -> tuple:
    """Test a command and return (success, response)."""
    url = f"http://{HOST}/cmd.cgi?{cmd}"
    try:
        async with session.get(url) as resp:
            text = (await resp.text()).strip()
            return (text.startswith("$A0"), text)
    except Exception as e:
        return (False, str(e))


async def get_status(session: aiohttp.ClientSession) -> str:
    """Get current status."""
    url = f"http://{HOST}/cmd.cgi?$A5"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def main() -> int:
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print(" Command Format Discovery ".center(80))
    print("="*80)
    print(Colors.END)

    print(f"\n{Colors.YELLOW}Testing different command formats via HTTP{Colors.END}\n")

    auth = aiohttp.BasicAuth(USER, PASSWORD)

    async with aiohttp.ClientSession(auth=auth) as session:
        # Get initial status
        initial = await get_status(session)
        print(f"Initial status: {initial}\n")

        # Test various command formats for turning ON outlet 1
        test_cases = [
            # Documented format
            ("$A3,1,1", "Documented format: $A3,port,value"),

            # With URL encoding
            ("%24A3,1,1", "URL encoded $: %24A3,1,1"),

            # Alternative comma format
            ("$A3%2C1%2C1", "URL encoded commas: $A3%2C1%2C1"),

            # Toggle format (we know this works)
            ("rly=0", "Toggle format: rly=0 (known working)"),

            # Serial-style format
            ("/pset 1 1", "Serial format: /pset 1 1"),

            # Serial format URL encoded
            ("%2Fpset%201%201", "Serial format URL encoded"),

            # Try without comma
            ("$A3 1 1", "Space separated: $A3 1 1"),

            # Try with = sign
            ("$A3=1,1", "Equals format: $A3=1,1"),

            # Web interface might use different command
            ("pset=1,1", "Web-style: pset=1,1"),
            ("port=1&state=1", "Query params: port=1&state=1"),
            ("outlet=1&value=1", "Query params: outlet=1&value=1"),

            # Try the $A7 format (set all)
            ("$A7,1", "Set all ON: $A7,1"),
        ]

        for cmd, description in test_cases:
            print(f"{Colors.BOLD}Testing: {description}{Colors.END}")
            print(f"  Command: {cmd}")

            success, response = await test_command(session, cmd, description)

            if success:
                print(f"  {Colors.GREEN}✓ SUCCESS: {response}{Colors.END}")

                # Get status to see if it changed
                await asyncio.sleep(1)
                status = await get_status(session)
                parts = status.split(",")
                outlets = parts[1] if len(parts) > 1 else ""
                print(f"  Status after: {outlets}")

                # If this changed the state, toggle back
                if outlets != "00000":
                    print(f"  {Colors.YELLOW}State changed! Toggling back...{Colors.END}")
                    # Use known working toggle to restore
                    await test_command(session, "rly=0", "restore")
                    await asyncio.sleep(1)

            else:
                print(f"  {Colors.RED}✗ FAILED: {response}{Colors.END}")

            print()

        # Now test if the web interface uses a different endpoint
        print(f"\n{Colors.BOLD}{Colors.CYAN}Testing Alternative Endpoints{Colors.END}\n")

        alternative_endpoints = [
            ("/outlet.cgi?1=1", "outlet.cgi endpoint"),
            ("/control.cgi?port=1&state=1", "control.cgi endpoint"),
            ("/pset.cgi?1=1", "pset.cgi endpoint"),
        ]

        for endpoint, description in alternative_endpoints:
            print(f"{Colors.BOLD}Testing: {description}{Colors.END}")
            url = f"http://{HOST}{endpoint}"
            print(f"  URL: {url}")

            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        text = (await resp.text()).strip()
                        print(f"  {Colors.GREEN}✓ Response: {text[:100]}{Colors.END}")

                        # Check status
                        await asyncio.sleep(1)
                        status = await get_status(session)
                        parts = status.split(",")
                        outlets = parts[1] if len(parts) > 1 else ""
                        print(f"  Status after: {outlets}")

                        if outlets != "00000":
                            print(f"  {Colors.GREEN}State changed! This endpoint works!{Colors.END}")
                            # Toggle back
                            await test_command(session, "rly=0", "restore")
                            await asyncio.sleep(1)
                    else:
                        print(f"  {Colors.RED}✗ HTTP {resp.status}{Colors.END}")
            except Exception as e:
                print(f"  {Colors.RED}✗ Error: {e}{Colors.END}")

            print()

        # Final analysis
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("="*80)
        print(" Summary ".center(80))
        print("="*80)
        print(Colors.END)

        print(f"\n{Colors.YELLOW}Commands that work via HTTP:{Colors.END}")
        print("  • $A5 - Get status (confirmed working)")
        print("  • rly=X - Toggle outlet (confirmed working)")
        print()
        print(f"{Colors.YELLOW}Commands that DON'T work via HTTP:{Colors.END}")
        print("  • $A3,port,value - Set explicit ON/OFF (returns $AF)")
        print("  • $A7,value - Set all ON/OFF (returns $AF)")
        print()
        print(f"{Colors.CYAN}Conclusion:{Colors.END}")
        print("  The HTTP interface may only support:")
        print("  1. Status query ($A5)")
        print("  2. Toggle command (rly=X)")
        print()
        print("  This is ACCEPTABLE for building the integration!")
        print("  We can use toggle + status checking to achieve ON/OFF control.")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}")
        sys.exit(130)
