#!/usr/bin/env python3
"""
Interactive Outlet Toggle Test
This script will help us map which rly=X command controls which physical outlet.

IMPORTANT: This script WILL change outlet states!
Make sure your loads can handle power cycling.
"""

import asyncio
import os
import sys
from typing import Optional
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = os.getenv("NETCOMMANDER_USER", "admin")
PASSWORD = os.getenv("NETCOMMANDER_PASSWORD", "admin")


class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def get_status(session: aiohttp.ClientSession) -> Optional[str]:
    """Get device status."""
    try:
        url = f"http://{HOST}/cmd.cgi?$A5"
        async with session.get(url) as resp:
            if resp.status == 200:
                return (await resp.text()).strip()
    except Exception as e:
        print(f"{Colors.RED}Error getting status: {e}{Colors.END}")
    return None


async def send_rly_command(session: aiohttp.ClientSession, rly_index: int) -> bool:
    """Send rly command to toggle outlet."""
    try:
        url = f"http://{HOST}/cmd.cgi?rly={rly_index}"
        print(f"{Colors.CYAN}Sending: rly={rly_index}{Colors.END}")
        async with session.get(url) as resp:
            if resp.status == 200:
                text = (await resp.text()).strip()
                print(f"{Colors.GREEN}Response: {text}{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}HTTP {resp.status}{Colors.END}")
                return False
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return False


async def main() -> int:
    """Main interactive test."""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("="*70)
    print(" Interactive Outlet Toggle Test ".center(70))
    print("="*70)
    print(Colors.END)

    print(f"\n{Colors.YELLOW}⚠ WARNING: This test WILL toggle outlets!{Colors.END}")
    print(f"{Colors.YELLOW}   Make sure connected loads can handle power cycling.{Colors.END}\n")

    response = input("Are you ready to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("Test cancelled.")
        return 0

    auth = aiohttp.BasicAuth(USER, PASSWORD)

    mapping = {}  # Will store rly_index -> physical_outlet mapping

    async with aiohttp.ClientSession(auth=auth) as session:
        # Get initial status
        print(f"\n{Colors.BOLD}Step 1: Get initial status{Colors.END}")
        initial_status = await get_status(session)
        if not initial_status:
            print(f"{Colors.RED}Failed to get initial status{Colors.END}")
            return 1

        parts = initial_status.split(",")
        initial_outlets = parts[1] if len(parts) > 1 else ""
        print(f"Initial outlet string: {Colors.BOLD}{initial_outlets}{Colors.END}")
        print(f"Total current: {parts[2] if len(parts) > 2 else 'N/A'}")

        # Test each rly index
        print(f"\n{Colors.BOLD}Step 2: Test each rly command{Colors.END}")
        print("For each rly index, we'll toggle it ON, you verify, then toggle OFF.\n")

        for rly_idx in range(5):  # 0-4 for 5 outlets
            print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}Testing rly={rly_idx}{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.END}")

            # Get status before
            before_status = await get_status(session)
            if not before_status:
                continue
            before_outlets = before_status.split(",")[1]
            print(f"Status before: {before_outlets}")

            # Toggle ON
            print(f"\n{Colors.GREEN}Toggling rly={rly_idx} (should turn an outlet ON){Colors.END}")
            await send_rly_command(session, rly_idx)
            await asyncio.sleep(1)  # Give device time

            # Get status after first toggle
            after_status = await get_status(session)
            if not after_status:
                continue
            after_outlets = after_status.split(",")[1]
            print(f"Status after:  {after_outlets}")

            # Show diff
            print(f"\n{Colors.BOLD}Bit changes:{Colors.END}")
            for i in range(len(before_outlets)):
                if before_outlets[i] != after_outlets[i]:
                    print(f"  Position {i}: {before_outlets[i]} → {after_outlets[i]} {Colors.GREEN}CHANGED{Colors.END}")

            # Ask user which physical outlet changed
            print(f"\n{Colors.YELLOW}{Colors.BOLD}LOOK AT YOUR PDU:{Colors.END}")
            print("Which PHYSICAL outlet turned ON?")
            print("(Enter outlet number 1-5, or 0 if none changed, or 's' to skip)")

            user_input = input("Physical outlet number: ").strip()

            if user_input.lower() == 's':
                print("Skipped.")
                continue

            try:
                physical_outlet = int(user_input)
                if 1 <= physical_outlet <= 5:
                    mapping[rly_idx] = physical_outlet
                    print(f"{Colors.GREEN}✓ Recorded: rly={rly_idx} → Physical outlet {physical_outlet}{Colors.END}")
                elif physical_outlet == 0:
                    print(f"{Colors.YELLOW}⚠ No change observed for rly={rly_idx}{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Invalid input{Colors.END}")

            # Toggle OFF to restore state
            print(f"\n{Colors.BLUE}Toggling rly={rly_idx} again (should turn it OFF){Colors.END}")
            await send_rly_command(session, rly_idx)
            await asyncio.sleep(1)

            # Verify it's off
            final_status = await get_status(session)
            if final_status:
                final_outlets = final_status.split(",")[1]
                print(f"Status after OFF: {final_outlets}")

            print()
            input("Press ENTER to continue to next relay...")

        # Show results
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("="*70)
        print(" Mapping Results ".center(70))
        print("="*70)
        print(Colors.END)

        print(f"\n{Colors.BOLD}Discovered Mapping:{Colors.END}")
        for rly_idx in sorted(mapping.keys()):
            phys = mapping[rly_idx]
            print(f"  rly={rly_idx} → Physical Outlet {phys}")

        # Derive status string mapping
        print(f"\n{Colors.BOLD}Now let's verify the status string mapping:{Colors.END}")
        print("We'll turn ON each physical outlet and see which bit changes.\n")

        status_mapping = {}

        for phys_outlet in range(1, 6):
            # Find the rly index for this physical outlet
            rly_idx = None
            for r, p in mapping.items():
                if p == phys_outlet:
                    rly_idx = r
                    break

            if rly_idx is None:
                print(f"{Colors.YELLOW}No rly mapping found for physical outlet {phys_outlet}{Colors.END}")
                continue

            print(f"{Colors.CYAN}Testing Physical Outlet {phys_outlet} (rly={rly_idx}){Colors.END}")

            # Get status before
            before_status = await get_status(session)
            before_outlets = before_status.split(",")[1]

            # Turn ON
            await send_rly_command(session, rly_idx)
            await asyncio.sleep(1)

            # Get status after
            after_status = await get_status(session)
            after_outlets = after_status.split(",")[1]

            # Find which position changed
            for i in range(len(before_outlets)):
                if before_outlets[i] != after_outlets[i]:
                    status_mapping[i] = phys_outlet
                    print(f"  Physical {phys_outlet} → Status position {i}")

            # Turn OFF
            await send_rly_command(session, rly_idx)
            await asyncio.sleep(1)

        # Final summary
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("="*70)
        print(" FINAL MAPPING SUMMARY ".center(70))
        print("="*70)
        print(Colors.END)

        print(f"\n{Colors.BOLD}Control Mapping (rly command → Physical outlet):{Colors.END}")
        for rly_idx in range(5):
            if rly_idx in mapping:
                print(f"  rly={rly_idx} controls Physical Outlet {mapping[rly_idx]}")

        print(f"\n{Colors.BOLD}Status Mapping (status string position → Physical outlet):{Colors.END}")
        for pos in range(5):
            if pos in status_mapping:
                print(f"  Status[{pos}] represents Physical Outlet {status_mapping[pos]}")

        print(f"\n{Colors.GREEN}Test complete!{Colors.END}")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted{Colors.END}")
        sys.exit(130)
