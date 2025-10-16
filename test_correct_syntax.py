#!/usr/bin/env python3
"""
Test the correct $A3 syntax we just discovered: SPACES not COMMAS!

Confirmed working: $A3 1 1 (turn outlet 1 ON)
Should also work: $A3 1 0 (turn outlet 1 OFF)
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


async def get_status(session: aiohttp.ClientSession) -> str:
    """Get device status."""
    url = f"http://{HOST}/cmd.cgi?$A5"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def set_outlet_explicit(session: aiohttp.ClientSession, port: int, value: int) -> str:
    """Set outlet using correct syntax: $A3 port value (SPACES!)"""
    url = f"http://{HOST}/cmd.cgi?$A3 {port} {value}"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def main() -> int:
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print(" Correct Syntax Verification ".center(80))
    print("="*80)
    print(Colors.END)

    print(f"\n{Colors.GREEN}✓ Discovered: $A3 command works with SPACES, not COMMAS!{Colors.END}")
    print(f"{Colors.GREEN}  Correct: $A3 1 1 (turn outlet 1 ON){Colors.END}")
    print(f"{Colors.RED}  Wrong:   $A3,1,1 (returns $AF){Colors.END}\n")

    auth = aiohttp.BasicAuth(USER, PASSWORD)

    async with aiohttp.ClientSession(auth=auth) as session:
        # Verify all outlets start OFF
        print(f"{Colors.BOLD}Initial State{Colors.END}")
        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""
        print(f"Status: {outlets}")

        if outlets != "00000":
            print(f"{Colors.YELLOW}Not all OFF, turning all off first...{Colors.END}")
            for i in range(1, 6):
                await set_outlet_explicit(session, i, 0)
                await asyncio.sleep(0.5)
            status = await get_status(session)
            parts = status.split(",")
            outlets = parts[1] if len(parts) > 1 else ""
            print(f"After turning all OFF: {outlets}")

        # Test turning ON outlet 1
        print(f"\n{Colors.BOLD}Test 1: Turn ON outlet 1 (explicit){Colors.END}")
        print(f"Command: $A3 1 1")
        response = await set_outlet_explicit(session, 1, 1)
        print(f"Response: {response}")

        if response.startswith("$A0"):
            print(f"{Colors.GREEN}✓ Command accepted{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Command failed: {response}{Colors.END}")
            return 1

        await asyncio.sleep(1)
        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""
        print(f"Status: {outlets}")

        print(f"\n{Colors.YELLOW}Physical check:{Colors.END}")
        led_on = input("  Is outlet 1 LED ON? (y/n): ").strip().lower() == 'y'
        has_power = input("  Does outlet 1 have POWER? (y/n): ").strip().lower() == 'y'

        if outlets[4] == '1' and led_on and has_power:
            print(f"\n{Colors.GREEN}✓✓✓ PERFECT! All aligned:{Colors.END}")
            print(f"{Colors.GREEN}  Status=1, LED=ON, Power=ON{Colors.END}")
        else:
            print(f"\n{Colors.RED}✗ Something doesn't match{Colors.END}")
            print(f"  Status bit: {outlets[4]}, LED: {'ON' if led_on else 'OFF'}, Power: {'ON' if has_power else 'OFF'}")

        # Test turning OFF outlet 1
        print(f"\n{Colors.BOLD}Test 2: Turn OFF outlet 1 (explicit){Colors.END}")
        print(f"Command: $A3 1 0")
        response = await set_outlet_explicit(session, 1, 0)
        print(f"Response: {response}")

        if response.startswith("$A0"):
            print(f"{Colors.GREEN}✓ Command accepted{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Command failed: {response}{Colors.END}")

        await asyncio.sleep(1)
        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""
        print(f"Status: {outlets}")

        led_on = input("  Is outlet 1 LED OFF now? (y/n): ").strip().lower() != 'y'
        has_power = input("  Does outlet 1 have NO power? (y/n): ").strip().lower() != 'y'

        if outlets[4] == '0' and not led_on and not has_power:
            print(f"\n{Colors.GREEN}✓✓✓ PERFECT! All aligned (OFF){Colors.END}")
            print(f"{Colors.GREEN}  Status=0, LED=OFF, Power=OFF{Colors.END}")
        else:
            print(f"\n{Colors.RED}✗ Something doesn't match{Colors.END}")

        # Test all outlets
        print(f"\n{Colors.BOLD}Test 3: Turn ON all outlets{Colors.END}")
        for port in range(1, 6):
            print(f"  Turning ON outlet {port}...")
            response = await set_outlet_explicit(session, port, 1)
            if not response.startswith("$A0"):
                print(f"  {Colors.RED}✗ Failed for outlet {port}{Colors.END}")
            await asyncio.sleep(0.5)

        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""
        print(f"Status: {outlets}")

        if outlets == "11111":
            print(f"{Colors.GREEN}✓ All outlets ON in status{Colors.END}")
        else:
            print(f"{Colors.YELLOW}? Unexpected: {outlets}{Colors.END}")

        all_on = input(f"\n{Colors.YELLOW}Are all 5 LEDs ON? (y/n): {Colors.END}").strip().lower() == 'y'

        if outlets == "11111" and all_on:
            print(f"\n{Colors.GREEN}✓✓✓ EXCELLENT! Explicit ON/OFF works perfectly!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}Some mismatch - needs investigation{Colors.END}")

        # Turn all OFF
        print(f"\n{Colors.BOLD}Test 4: Turn OFF all outlets{Colors.END}")
        for port in range(1, 6):
            print(f"  Turning OFF outlet {port}...")
            response = await set_outlet_explicit(session, port, 0)
            if not response.startswith("$A0"):
                print(f"  {Colors.RED}✗ Failed for outlet {port}{Colors.END}")
            await asyncio.sleep(0.5)

        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""
        print(f"Status: {outlets}")

        if outlets == "00000":
            print(f"{Colors.GREEN}✓ All outlets OFF in status{Colors.END}")

        all_off = input(f"\n{Colors.YELLOW}Are all 5 LEDs OFF? (y/n): {Colors.END}").strip().lower() == 'y'

        # Final summary
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("="*80)
        print(" SUMMARY ".center(80))
        print("="*80)
        print(Colors.END)

        print(f"\n{Colors.GREEN}{Colors.BOLD}WORKING COMMANDS:{Colors.END}")
        print(f"  • $A5 - Get status")
        print(f"  • $A3 port value - Explicit ON/OFF (with SPACES!)")
        print(f"    - $A3 1 1 = Turn outlet 1 ON")
        print(f"    - $A3 1 0 = Turn outlet 1 OFF")
        print(f"  • rly=X - Toggle outlet X")
        print()
        print(f"{Colors.GREEN}This gives us FULL control!{Colors.END}")
        print(f"{Colors.GREEN}We can build a complete integration with these commands.{Colors.END}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}")
        sys.exit(130)
