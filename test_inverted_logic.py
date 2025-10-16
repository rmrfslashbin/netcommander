#!/usr/bin/env python3
"""
Test for inverted outlet logic on outlets 1 and 5.

Current situation:
- Physical outlets 1 and 5 are ON (have power)
- Device reports all outlets as OFF (00000)

This test will help determine if control commands are also inverted.
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


async def send_command(session: aiohttp.ClientSession, cmd: str) -> str:
    """Send a command to the device."""
    url = f"http://{HOST}/cmd.cgi?{cmd}"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def main() -> int:
    print(f"{Colors.BOLD}{Colors.RED}")
    print("="*70)
    print(" INVERTED LOGIC TEST ".center(70))
    print("="*70)
    print(Colors.END)

    print(f"\n{Colors.YELLOW}Current Situation:{Colors.END}")
    print("  • Physical outlet 1: ON (has power)")
    print("  • Physical outlet 5: ON (has power)")
    print("  • Device reports: All outlets OFF")
    print()

    auth = aiohttp.BasicAuth(USER, PASSWORD)

    async with aiohttp.ClientSession(auth=auth) as session:
        # Verify current state
        print(f"{Colors.CYAN}Step 1: Verify current status{Colors.END}")
        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""
        print(f"  Device reports: {outlets}")
        print(f"  Physical reality: outlet 1=ON, outlet 5=ON")
        print()

        # Test different command formats
        print(f"{Colors.CYAN}Step 2: Discover which outlet numbers map to physical 1 and 5{Colors.END}")
        print("We'll try different rly indices to see which control physical outlets 1 and 5\n")

        print(f"{Colors.YELLOW}Testing Physical Outlet 1 (currently ON){Colors.END}")
        print("We'll try toggling different rly indices and you tell me if outlet 1 turned OFF\n")

        for rly_idx in range(5):
            print(f"{Colors.BOLD}Test rly={rly_idx}:{Colors.END}")

            # Get status before
            before = await get_status(session)
            before_outlets = before.split(",")[1]
            print(f"  Before: {before_outlets}")

            # Toggle
            print(f"  Sending: rly={rly_idx}")
            await send_command(session, f"rly={rly_idx}")
            await asyncio.sleep(1)

            # Get status after
            after = await get_status(session)
            after_outlets = after.split(",")[1]
            print(f"  After:  {after_outlets}")

            # Show what changed in the status
            changed_positions = []
            for i in range(len(before_outlets)):
                if before_outlets[i] != after_outlets[i]:
                    changed_positions.append(i)

            if changed_positions:
                print(f"  Status bits that changed: {changed_positions}")
            else:
                print(f"  No status change detected")

            # Ask user about physical reality
            print(f"\n  {Colors.YELLOW}Look at Physical Outlet 1:{Colors.END}")
            user_input = input("  Did physical outlet 1 change state? (y/n/q to quit): ").strip().lower()

            if user_input == 'q':
                print("\nTest aborted")
                return 0
            elif user_input == 'y':
                print(f"  {Colors.GREEN}✓ Found: rly={rly_idx} controls Physical Outlet 1{Colors.END}")
                print(f"  {Colors.GREEN}  Status position {changed_positions[0] if changed_positions else '?'} represents outlet 1{Colors.END}")

                # Determine if inverted
                if before_outlets[changed_positions[0]] == '0' and after_outlets[changed_positions[0]] == '1':
                    print(f"  {Colors.RED}  ⚠ INVERTED LOGIC: Device said OFF→ON, but physical was ON→OFF{Colors.END}")
                elif before_outlets[changed_positions[0]] == '1' and after_outlets[changed_positions[0]] == '0':
                    print(f"  {Colors.GREEN}  Normal logic: Device said ON→OFF, physical was ON→OFF{Colors.END}")

                # Toggle back
                print(f"\n  Toggling back...")
                await send_command(session, f"rly={rly_idx}")
                await asyncio.sleep(1)

                restore = await get_status(session)
                restore_outlets = restore.split(",")[1]
                print(f"  After restore: {restore_outlets}")

                break
            else:
                # Toggle back to restore state
                print(f"  Toggling back to restore state...")
                await send_command(session, f"rly={rly_idx}")
                await asyncio.sleep(1)

            print()

        # Now test outlet 5
        print(f"\n{Colors.YELLOW}Testing Physical Outlet 5 (currently ON){Colors.END}")
        print("Press ENTER to continue or 'q' to quit: ", end='')
        if input().strip().lower() == 'q':
            return 0

        for rly_idx in range(5):
            print(f"\n{Colors.BOLD}Test rly={rly_idx}:{Colors.END}")

            before = await get_status(session)
            before_outlets = before.split(",")[1]
            print(f"  Before: {before_outlets}")

            print(f"  Sending: rly={rly_idx}")
            await send_command(session, f"rly={rly_idx}")
            await asyncio.sleep(1)

            after = await get_status(session)
            after_outlets = after.split(",")[1]
            print(f"  After:  {after_outlets}")

            changed_positions = []
            for i in range(len(before_outlets)):
                if before_outlets[i] != after_outlets[i]:
                    changed_positions.append(i)

            if changed_positions:
                print(f"  Status bits that changed: {changed_positions}")

            print(f"\n  {Colors.YELLOW}Look at Physical Outlet 5:{Colors.END}")
            user_input = input("  Did physical outlet 5 change state? (y/n/q to quit): ").strip().lower()

            if user_input == 'q':
                print("\nTest aborted")
                return 0
            elif user_input == 'y':
                print(f"  {Colors.GREEN}✓ Found: rly={rly_idx} controls Physical Outlet 5{Colors.END}")
                print(f"  {Colors.GREEN}  Status position {changed_positions[0] if changed_positions else '?'} represents outlet 5{Colors.END}")

                if changed_positions:
                    if before_outlets[changed_positions[0]] == '0' and after_outlets[changed_positions[0]] == '1':
                        print(f"  {Colors.RED}  ⚠ INVERTED LOGIC: Device said OFF→ON, but physical was ON→OFF{Colors.END}")
                    elif before_outlets[changed_positions[0]] == '1' and after_outlets[changed_positions[0]] == '0':
                        print(f"  {Colors.GREEN}  Normal logic: Device said ON→OFF, physical was ON→OFF{Colors.END}")

                print(f"\n  Toggling back...")
                await send_command(session, f"rly={rly_idx}")
                await asyncio.sleep(1)

                restore = await get_status(session)
                print(f"  After restore: {restore.split(',')[1]}")

                break
            else:
                print(f"  Toggling back...")
                await send_command(session, f"rly={rly_idx}")
                await asyncio.sleep(1)

        print(f"\n{Colors.BOLD}{Colors.GREEN}Test complete!{Colors.END}")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}")
        sys.exit(130)
