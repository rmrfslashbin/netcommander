#!/usr/bin/env python3
"""
Test explicit ON/OFF commands ($A3) to see if they can fix the inverted state.

The device might be in a confused state where toggle (rly=X) doesn't work properly,
but explicit commands ($A3,port,value) might reset it correctly.
"""

import asyncio
import os
import sys
import aiohttp
from dotenv import load_dotenv

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


async def get_status(session: aiohttp.ClientSession) -> str:
    """Get device status."""
    url = f"http://{HOST}/cmd.cgi?$A5"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def send_explicit_command(session: aiohttp.ClientSession, port: int, value: int) -> str:
    """Send $A3 command to set outlet explicitly ON (1) or OFF (0)."""
    url = f"http://{HOST}/cmd.cgi?$A3,{port},{value}"
    print(f"{Colors.CYAN}Sending: $A3,{port},{value} (Port {port} → {'ON' if value == 1 else 'OFF'}){Colors.END}")
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def send_set_all(session: aiohttp.ClientSession, value: int) -> str:
    """Send $A7 command to set all outlets ON (1) or OFF (0)."""
    url = f"http://{HOST}/cmd.cgi?$A7,{value}"
    print(f"{Colors.CYAN}Sending: $A7,{value} (ALL outlets → {'ON' if value == 1 else 'OFF'}){Colors.END}")
    async with session.get(url) as resp:
        return (await resp.text()).strip()


def display_status(status_str: str) -> None:
    """Display status nicely."""
    parts = status_str.split(",")
    if len(parts) >= 3:
        outlets = parts[1]
        current = parts[2]
        print(f"{Colors.BOLD}Status:{Colors.END} {outlets} | Current: {current}A")
    else:
        print(f"{Colors.BOLD}Status:{Colors.END} {status_str}")


async def main() -> int:
    """Main test function."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print(" Explicit Command Test - Attempting to Fix Inverted State ".center(80))
    print("="*80)
    print(Colors.END)

    print(f"\n{Colors.YELLOW}Strategy:{Colors.END}")
    print("1. Check current status (should show 00000 but outlets have power)")
    print("2. Send explicit ON commands ($A3,port,1) to 'align' device state with reality")
    print("3. Verify if status now matches physical power state")
    print()

    auth = aiohttp.BasicAuth(USER, PASSWORD)

    async with aiohttp.ClientSession(auth=auth) as session:
        # Step 1: Check initial status
        print(f"{Colors.BOLD}Step 1: Check Initial Status{Colors.END}")
        status = await get_status(session)
        display_status(status)

        parts = status.split(",")
        initial_outlets = parts[1] if len(parts) > 1 else ""

        print(f"\n{Colors.YELLOW}Physical reality: Outlets have power (but LEDs are OFF){Colors.END}")
        print(f"{Colors.YELLOW}Device reports: {initial_outlets} (all OFF){Colors.END}")
        print(f"{Colors.YELLOW}This is the INVERTED state we want to fix{Colors.END}")

        # Step 2: Try explicit ON command for outlet 1
        print(f"\n{Colors.BOLD}Step 2: Send Explicit ON Command to Outlet 1{Colors.END}")
        print(f"{Colors.CYAN}Hypothesis: Sending $A3,1,1 (explicit ON) might sync the device{Colors.END}")

        response = await send_explicit_command(session, 1, 1)
        print(f"Response: {response}")
        await asyncio.sleep(1.5)

        status = await get_status(session)
        display_status(status)

        print(f"\n{Colors.YELLOW}Check physical outlet 1:{Colors.END}")
        led_on = input("  Is the LED now ON? (y/n): ").strip().lower() == 'y'
        has_power = input("  Does it still have POWER? (y/n): ").strip().lower() == 'y'

        print(f"\n  LED: {'ON' if led_on else 'OFF'}")
        print(f"  Power: {'ON' if has_power else 'OFF'}")

        after_parts = status.split(",")
        after_outlets = after_parts[1] if len(after_parts) > 1 else ""

        if after_outlets[4] == '1':  # Position 4 is outlet 1
            print(f"  Device now reports outlet 1 as: {Colors.GREEN}ON (1){Colors.END}")
            if has_power and led_on:
                print(f"\n{Colors.GREEN}✓ SUCCESS! Device state aligned with reality!{Colors.END}")
                print(f"{Colors.GREEN}  LED matches power, status shows ON, outlet has power{Colors.END}")
            elif has_power and not led_on:
                print(f"\n{Colors.YELLOW}⚠ Partial success: Has power, but LED still off{Colors.END}")
            else:
                print(f"\n{Colors.RED}✗ Still inverted: Status says ON but no power{Colors.END}")
        else:
            print(f"  Device still reports outlet 1 as: {Colors.RED}OFF (0){Colors.END}")

        # Step 3: Try turning it OFF explicitly
        print(f"\n{Colors.BOLD}Step 3: Send Explicit OFF Command to Outlet 1{Colors.END}")

        response = await send_explicit_command(session, 1, 0)
        print(f"Response: {response}")
        await asyncio.sleep(1.5)

        status = await get_status(session)
        display_status(status)

        print(f"\n{Colors.YELLOW}Check physical outlet 1 again:{Colors.END}")
        led_on = input("  Is the LED now ON? (y/n): ").strip().lower() == 'y'
        has_power = input("  Does it still have POWER? (y/n): ").strip().lower() == 'y'

        print(f"\n  LED: {'ON' if led_on else 'OFF'}")
        print(f"  Power: {'ON' if has_power else 'OFF'}")

        # Step 4: Try the $A7 "set all" command
        print(f"\n{Colors.BOLD}Step 4: Try 'Set All ON' Command ($A7,1){Colors.END}")
        print(f"{Colors.CYAN}This might force-sync all outlets{Colors.END}")

        response = await send_set_all(session, 1)
        print(f"Response: {response}")
        await asyncio.sleep(1.5)

        status = await get_status(session)
        display_status(status)

        print(f"\n{Colors.YELLOW}Observe all outlets:{Colors.END}")
        print("  Are all LEDs now ON? ", end='')
        all_leds_on = input("(y/n): ").strip().lower() == 'y'
        print("  Do all outlets have POWER? ", end='')
        all_power = input("(y/n): ").strip().lower() == 'y'

        after_parts = status.split(",")
        after_outlets = after_parts[1] if len(after_parts) > 1 else ""

        if after_outlets == "11111":
            print(f"\n{Colors.GREEN}Device reports: 11111 (all ON){Colors.END}")
            if all_leds_on and all_power:
                print(f"{Colors.GREEN}✓ SUCCESS! All aligned - LEDs ON, Power ON, Status ON{Colors.END}")
            elif all_power and not all_leds_on:
                print(f"{Colors.YELLOW}⚠ Has power but LEDs still off{Colors.END}")
            else:
                print(f"{Colors.RED}✗ Still inverted{Colors.END}")
        else:
            print(f"\n{Colors.RED}Device reports: {after_outlets} (not all ON){Colors.END}")

        # Step 5: Turn all OFF and check
        print(f"\n{Colors.BOLD}Step 5: Turn All OFF ($A7,0){Colors.END}")

        response = await send_set_all(session, 0)
        print(f"Response: {response}")
        await asyncio.sleep(1.5)

        status = await get_status(session)
        display_status(status)

        print(f"\n{Colors.YELLOW}Final check:{Colors.END}")
        print("  Are all LEDs now OFF? ", end='')
        all_leds_off = input("(y/n): ").strip().lower() == 'y'
        print("  Do all outlets have NO power? ", end='')
        all_no_power = input("(y/n): ").strip().lower() == 'y'

        after_parts = status.split(",")
        after_outlets = after_parts[1] if len(after_parts) > 1 else ""

        print(f"\n{Colors.BOLD}FINAL ASSESSMENT:{Colors.END}")
        print(f"Device reports: {after_outlets}")
        print(f"LEDs: {'All OFF' if all_leds_off else 'Some ON'}")
        print(f"Power: {'All OFF' if all_no_power else 'Some ON'}")

        if after_outlets == "00000" and all_leds_off and all_no_power:
            print(f"\n{Colors.GREEN}✓✓✓ DEVICE IS FIXED! All states aligned!{Colors.END}")
            print(f"{Colors.GREEN}Status=OFF, LEDs=OFF, Power=OFF - Everything matches!{Colors.END}")
        elif after_outlets == "00000" and all_leds_off and not all_no_power:
            print(f"\n{Colors.RED}✗✗✗ STILL INVERTED - Status/LED say OFF but outlets have power{Colors.END}")
            print(f"{Colors.RED}Explicit commands did NOT fix the issue{Colors.END}")
            print(f"\n{Colors.YELLOW}RECOMMENDATION: Factory reset required{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}⚠ Mixed results - needs more investigation{Colors.END}")

    print(f"\n{Colors.BOLD}Test complete{Colors.END}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}")
        sys.exit(130)
