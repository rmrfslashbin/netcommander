#!/usr/bin/env python3
"""
Comprehensive Outlet Mapping Test

For each physical outlet (1-5), this test will:
1. Record initial LED state (user observes)
2. Record initial power state (user tests with load/meter)
3. Record device status response
4. Toggle the outlet
5. Record new LED state
6. Record new power state
7. Record new device status
8. Toggle again
9. Record final states

This gives us a complete picture of:
- Which rly command controls which outlet
- LED vs actual power correlation
- Device status vs reality correlation
- Any inverted logic patterns
"""

import asyncio
import os
import sys
import json
from typing import Optional
import aiohttp
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = os.getenv("NETCOMMANDER_USER", "admin")
PASSWORD = os.getenv("NETCOMMANDER_PASSWORD", "admin")


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")


def print_section(text: str) -> None:
    """Print formatted section."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD} {text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.END}\n")


async def get_status(session: aiohttp.ClientSession) -> Optional[str]:
    """Get device status via $A5 command."""
    try:
        url = f"http://{HOST}/cmd.cgi?$A5"
        async with session.get(url) as resp:
            if resp.status == 200:
                return (await resp.text()).strip()
    except Exception as e:
        print(f"{Colors.RED}Error getting status: {e}{Colors.END}")
    return None


async def toggle_outlet(session: aiohttp.ClientSession, rly_index: int) -> bool:
    """Send rly command to toggle outlet."""
    try:
        url = f"http://{HOST}/cmd.cgi?rly={rly_index}"
        async with session.get(url) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"{Colors.RED}Error toggling outlet: {e}{Colors.END}")
        return False


def get_user_bool(prompt: str, default: Optional[bool] = None) -> bool:
    """Get yes/no input from user."""
    suffix = " (Y/n)" if default is True else " (y/N)" if default is False else " (y/n)"

    while True:
        response = input(f"{Colors.YELLOW}{prompt}{suffix}: {Colors.END}").strip().lower()

        if not response and default is not None:
            return default

        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print(f"{Colors.RED}Please enter 'y' or 'n'{Colors.END}")


def parse_status(status_str: str) -> dict:
    """Parse status string into components."""
    parts = status_str.split(",")
    return {
        "raw": status_str,
        "code": parts[0] if len(parts) > 0 else "",
        "outlets": parts[1] if len(parts) > 1 else "",
        "current": parts[2] if len(parts) > 2 else "",
        "temp": parts[3] if len(parts) > 3 else "",
    }


def display_status(status: dict, highlight_pos: Optional[int] = None) -> None:
    """Display parsed status with optional highlighting."""
    outlets = status["outlets"]
    print(f"{Colors.BOLD}Device Status:{Colors.END} {status['code']}, ", end="")

    # Display outlet string with highlighting
    for i, bit in enumerate(outlets):
        if i == highlight_pos:
            color = Colors.GREEN if bit == "1" else Colors.RED
            print(f"{color}{Colors.BOLD}[{bit}]{Colors.END}", end="")
        else:
            print(bit, end="")

    print(f", {status['current']}A, {status['temp']}°C")


async def test_outlet(session: aiohttp.ClientSession, outlet_num: int, rly_index: int) -> dict:
    """Comprehensive test of a single outlet."""
    print_section(f"Testing Physical Outlet {outlet_num} (rly={rly_index})")

    results = {
        "outlet_number": outlet_num,
        "rly_index": rly_index,
        "status_position": None,
        "states": []
    }

    # State 1: Initial observation
    print(f"{Colors.BOLD}State 1: Initial Observation{Colors.END}")
    print("Please observe the physical PDU:\n")

    led_on = get_user_bool(f"  Is the LED indicator for outlet {outlet_num} ON?")
    has_power = get_user_bool(f"  Does outlet {outlet_num} have POWER? (test with load/meter)")

    status = await get_status(session)
    if not status:
        print(f"{Colors.RED}Failed to get device status{Colors.END}")
        return results

    parsed = parse_status(status)

    state1 = {
        "stage": "initial",
        "led_on": led_on,
        "has_power": has_power,
        "device_status": parsed,
    }
    results["states"].append(state1)

    print(f"\n  {Colors.CYAN}Recorded:{Colors.END}")
    print(f"    LED: {Colors.GREEN}ON{Colors.END}" if led_on else f"    LED: {Colors.RED}OFF{Colors.END}")
    print(f"    Power: {Colors.GREEN}ON{Colors.END}" if has_power else f"    Power: {Colors.RED}OFF{Colors.END}")
    display_status(parsed)

    # State 2: After first toggle
    print(f"\n{Colors.BOLD}State 2: After First Toggle{Colors.END}")
    print(f"  Sending command: rly={rly_index}")

    if not await toggle_outlet(session, rly_index):
        print(f"{Colors.RED}Toggle command failed{Colors.END}")
        return results

    await asyncio.sleep(1.5)  # Give device time to settle

    print("\nPlease observe the physical PDU again:\n")

    led_on = get_user_bool(f"  Is the LED indicator for outlet {outlet_num} ON?")
    has_power = get_user_bool(f"  Does outlet {outlet_num} have POWER?")

    status = await get_status(session)
    if not status:
        print(f"{Colors.RED}Failed to get device status{Colors.END}")
        return results

    parsed = parse_status(status)

    state2 = {
        "stage": "after_toggle_1",
        "led_on": led_on,
        "has_power": has_power,
        "device_status": parsed,
    }
    results["states"].append(state2)

    print(f"\n  {Colors.CYAN}Recorded:{Colors.END}")
    print(f"    LED: {Colors.GREEN}ON{Colors.END}" if led_on else f"    LED: {Colors.RED}OFF{Colors.END}")
    print(f"    Power: {Colors.GREEN}ON{Colors.END}" if has_power else f"    Power: {Colors.RED}OFF{Colors.END}")

    # Detect which status bit changed
    outlets1 = state1["device_status"]["outlets"]
    outlets2 = state2["device_status"]["outlets"]

    changed_positions = []
    for i in range(min(len(outlets1), len(outlets2))):
        if outlets1[i] != outlets2[i]:
            changed_positions.append(i)

    if changed_positions:
        pos = changed_positions[0]
        results["status_position"] = pos
        print(f"  {Colors.GREEN}✓ Status bit {pos} changed: '{outlets1[pos]}' → '{outlets2[pos]}'{Colors.END}")
        display_status(parsed, highlight_pos=pos)
    else:
        print(f"  {Colors.YELLOW}⚠ No status bits changed{Colors.END}")
        display_status(parsed)

    # State 3: After second toggle (should return to initial)
    print(f"\n{Colors.BOLD}State 3: After Second Toggle (returning to initial){Colors.END}")
    print(f"  Sending command: rly={rly_index}")

    if not await toggle_outlet(session, rly_index):
        print(f"{Colors.RED}Toggle command failed{Colors.END}")
        return results

    await asyncio.sleep(1.5)

    print("\nPlease observe the physical PDU one more time:\n")

    led_on = get_user_bool(f"  Is the LED indicator for outlet {outlet_num} ON?")
    has_power = get_user_bool(f"  Does outlet {outlet_num} have POWER?")

    status = await get_status(session)
    if not status:
        print(f"{Colors.RED}Failed to get device status{Colors.END}")
        return results

    parsed = parse_status(status)

    state3 = {
        "stage": "after_toggle_2",
        "led_on": led_on,
        "has_power": has_power,
        "device_status": parsed,
    }
    results["states"].append(state3)

    print(f"\n  {Colors.CYAN}Recorded:{Colors.END}")
    print(f"    LED: {Colors.GREEN}ON{Colors.END}" if led_on else f"    LED: {Colors.RED}OFF{Colors.END}")
    print(f"    Power: {Colors.GREEN}ON{Colors.END}" if has_power else f"    Power: {Colors.RED}OFF{Colors.END}")

    if results["status_position"] is not None:
        display_status(parsed, highlight_pos=results["status_position"])
    else:
        display_status(parsed)

    # Verify we're back to initial state
    if (state1["led_on"] == state3["led_on"] and
        state1["has_power"] == state3["has_power"] and
        state1["device_status"]["outlets"] == state3["device_status"]["outlets"]):
        print(f"\n  {Colors.GREEN}✓ Successfully returned to initial state{Colors.END}")
    else:
        print(f"\n  {Colors.YELLOW}⚠ State after two toggles differs from initial{Colors.END}")

    return results


def analyze_results(all_results: list) -> None:
    """Analyze all test results and display findings."""
    print_header("Analysis Results")

    # Mapping table
    print(f"{Colors.BOLD}Control to Outlet Mapping:{Colors.END}\n")
    print(f"{'rly Index':<12} {'→':<5} {'Physical Outlet':<20} {'Status Position':<20}")
    print("─" * 60)

    for result in all_results:
        rly = result["rly_index"]
        outlet = result["outlet_number"]
        pos = result["status_position"] if result["status_position"] is not None else "Unknown"
        print(f"rly={rly:<8} {'→':<5} Outlet {outlet:<15} Position {pos}")

    # Inverted logic detection
    print(f"\n{Colors.BOLD}Logic Inversion Analysis:{Colors.END}\n")

    for result in all_results:
        outlet = result["outlet_number"]

        if len(result["states"]) < 2:
            continue

        state1 = result["states"][0]
        state2 = result["states"][1]

        # Check if status matches reality
        if result["status_position"] is not None:
            pos = result["status_position"]

            status1_bit = state1["device_status"]["outlets"][pos]
            status2_bit = state2["device_status"]["outlets"][pos]

            # Status bit: 1=ON, 0=OFF
            status1_on = (status1_bit == "1")
            status2_on = (status2_bit == "1")

            # Physical reality
            power1 = state1["has_power"]
            power2 = state2["has_power"]

            # Check if they match
            matches_initial = (status1_on == power1)
            matches_after = (status2_on == power2)

            if matches_initial and matches_after:
                print(f"  Outlet {outlet}: {Colors.GREEN}✓ Normal logic - status matches power{Colors.END}")
            elif not matches_initial and not matches_after:
                print(f"  Outlet {outlet}: {Colors.RED}⚠ INVERTED logic - status opposite of power{Colors.END}")
            else:
                print(f"  Outlet {outlet}: {Colors.YELLOW}? Inconsistent - status sometimes matches{Colors.END}")

            # LED analysis
            led1 = state1["led_on"]
            led2 = state2["led_on"]

            if (led1 == power1) and (led2 == power2):
                print(f"               {Colors.GREEN}✓ LED matches power state{Colors.END}")
            elif (led1 == status1_on) and (led2 == status2_on):
                print(f"               {Colors.CYAN}ℹ LED matches device status (not power){Colors.END}")
            else:
                print(f"               {Colors.YELLOW}? LED behavior unclear{Colors.END}")


async def main() -> int:
    """Main test function."""
    print_header("Comprehensive Outlet Mapping Test")

    print(f"{Colors.CYAN}This test will systematically check all 5 outlets.{Colors.END}")
    print(f"{Colors.CYAN}For each outlet, you'll observe LED and power states.{Colors.END}\n")

    print(f"{Colors.YELLOW}⚠ This test will toggle each outlet twice.{Colors.END}")
    print(f"{Colors.YELLOW}  Make sure connected loads can handle power cycling.{Colors.END}\n")

    response = input("Ready to begin? (yes/no): ")
    if response.lower() != "yes":
        print("Test cancelled.")
        return 0

    auth = aiohttp.BasicAuth(USER, PASSWORD)
    all_results = []

    async with aiohttp.ClientSession(auth=auth) as session:
        # Test each outlet
        for outlet_num in range(1, 6):
            rly_index = outlet_num - 1  # Hypothesis: rly=0 controls outlet 1

            result = await test_outlet(session, outlet_num, rly_index)
            all_results.append(result)

            if outlet_num < 5:
                print(f"\n{Colors.BOLD}Press ENTER to continue to next outlet (or 'q' to quit)...{Colors.END}")
                user_input = input()
                if user_input.lower() == 'q':
                    break

    # Analyze and display results
    analyze_results(all_results)

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outlet_mapping_results_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{Colors.GREEN}✓ Results saved to: {filename}{Colors.END}")

    print_header("Test Complete")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
