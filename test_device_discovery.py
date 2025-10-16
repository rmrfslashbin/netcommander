#!/usr/bin/env python3
"""
Physical Device Discovery Test Script - READ ONLY
Tests the NP-0501DU to understand outlet mapping and API responses.

Expected initial state: Physical outlets 1 and 5 are ON
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
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_section(text: str) -> None:
    """Print a formatted section header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.END}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


async def test_connection(session: aiohttp.ClientSession) -> bool:
    """Test basic connectivity to device."""
    print_section("Connection Test")
    try:
        url = f"http://{HOST}/cmd.cgi?$A5"
        print_info(f"Testing connection to: {HOST}")
        print_info(f"URL: {url}")

        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            print_info(f"HTTP Status: {resp.status}")
            print_info(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print_info(f"Server: {resp.headers.get('Server', 'N/A')}")

            if resp.status == 200:
                print_success("Connection successful!")
                return True
            else:
                print_error(f"Unexpected status code: {resp.status}")
                return False

    except asyncio.TimeoutError:
        print_error(f"Connection timeout to {HOST}")
        return False
    except aiohttp.ClientConnectorError as e:
        print_error(f"Cannot connect to {HOST}: {e}")
        return False
    except Exception as e:
        print_error(f"Connection error: {e}")
        return False


async def get_status(session: aiohttp.ClientSession) -> Optional[str]:
    """Get device status using $A5 command."""
    print_section("Status Query ($A5)")
    try:
        url = f"http://{HOST}/cmd.cgi?$A5"
        print_info(f"Sending: $A5 (Get Outlet Status)")

        async with session.get(url) as resp:
            if resp.status == 200:
                status = await resp.text()
                print_success(f"Raw Response: {repr(status)}")
                return status.strip()
            else:
                print_error(f"HTTP {resp.status}")
                return None

    except Exception as e:
        print_error(f"Error: {e}")
        return None


def parse_status(status_str: str) -> dict:
    """Parse the status string from $A5 command."""
    print_section("Status String Analysis")

    print_info(f"Raw status: {repr(status_str)}")
    parts = status_str.split(",")
    print_info(f"Split by comma: {parts}")

    if len(parts) < 3:
        print_error(f"Unexpected format - expected at least 3 parts, got {len(parts)}")
        return {}

    result = {
        "response_code": parts[0],
        "outlets_raw": parts[1] if len(parts) > 1 else "",
        "total_current": parts[2] if len(parts) > 2 else "",
        "temperature": parts[3] if len(parts) > 3 else "",
    }

    print_info(f"Response Code: {result['response_code']}")
    print_info(f"Outlets String: {result['outlets_raw']}")
    print_info(f"Total Current: {result['total_current']}")
    print_info(f"Temperature: {result['temperature']}")

    # Parse outlet states
    outlets_str = result['outlets_raw']
    if outlets_str:
        print_section("Outlet State Breakdown")
        print_info(f"Outlet string length: {len(outlets_str)} characters")
        print_info(f"Documentation says: 'most right x for relay1'")
        print()

        # Parse left-to-right
        print(f"{Colors.BOLD}Left-to-Right parsing (index 0 = leftmost):{Colors.END}")
        for idx, state in enumerate(outlets_str):
            state_text = f"{Colors.GREEN}ON{Colors.END}" if state == "1" else f"{Colors.RED}OFF{Colors.END}"
            print(f"  Position {idx}: '{state}' = {state_text}")

        print()
        print(f"{Colors.BOLD}Right-to-Left parsing (per documentation):{Colors.END}")
        print(f"  'Most right x for relay1' means:")
        for idx, state in enumerate(reversed(outlets_str)):
            position = len(outlets_str) - 1 - idx
            relay_num = idx + 1
            state_text = f"{Colors.GREEN}ON{Colors.END}" if state == "1" else f"{Colors.RED}OFF{Colors.END}"
            print(f"  Position {position} (right-{idx}): '{state}' = Relay {relay_num} = {state_text}")

        # Create mapping
        result['outlets'] = {}
        for idx, state in enumerate(outlets_str):
            result['outlets'][idx] = (state == "1")

    return result


async def test_all_status_endpoints(session: aiohttp.ClientSession) -> None:
    """Try various endpoints to discover what's available."""
    print_section("API Endpoint Discovery")

    endpoints = [
        ("$A5", "Get Outlet Status"),
        ("$A1,admin,admin", "Login (may not work via HTTP)"),
        ("ver", "Version info (guess)"),
        ("help", "Help command (guess)"),
        ("status", "Status (guess)"),
    ]

    for cmd, description in endpoints:
        print_info(f"Testing: {cmd} - {description}")
        url = f"http://{HOST}/cmd.cgi?{cmd}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    print_success(f"  Response: {repr(text[:100])}")
                else:
                    print_warning(f"  HTTP {resp.status}")
        except asyncio.TimeoutError:
            print_warning(f"  Timeout")
        except Exception as e:
            print_warning(f"  Error: {e}")

        await asyncio.sleep(0.5)  # Be nice to the device


async def verify_physical_state(session: aiohttp.ClientSession) -> None:
    """Verify the current physical state matches expectations."""
    print_section("Physical State Verification")

    print_warning("IMPORTANT: Before running this test, verify:")
    print("  - Physical outlet 1: Should be ON (has load)")
    print("  - Physical outlet 5: Should be ON (has load)")
    print("  - Physical outlets 2, 3, 4: Should be OFF")
    print()

    status = await get_status(session)
    if not status:
        print_error("Could not get status")
        return

    parsed = parse_status(status)

    if not parsed.get('outlets'):
        print_error("Could not parse outlet states")
        return

    print_section("Mapping Analysis")
    print_info("Expected: Physical 1=ON, 5=ON, others=OFF")
    print()

    outlets_str = parsed['outlets_raw']

    # Test hypothesis 1: Index 0 = Physical outlet 1
    print(f"{Colors.BOLD}Hypothesis 1: Direct mapping (index 0 = Physical 1){Colors.END}")
    print(f"  Index 0: {outlets_str[0]} → Physical 1 (expected: 1/ON)")
    print(f"  Index 4: {outlets_str[4]} → Physical 5 (expected: 1/ON)")
    matches_h1 = outlets_str[0] == "1" and outlets_str[4] == "1"
    if matches_h1:
        print_success("✓ This hypothesis MATCHES!")
    else:
        print_error("✗ This hypothesis does NOT match")

    print()

    # Test hypothesis 2: Reversed mapping (index 0 = Physical 5)
    print(f"{Colors.BOLD}Hypothesis 2: Reversed mapping (index 0 = Physical 5){Colors.END}")
    print(f"  Index 0: {outlets_str[0]} → Physical 5 (expected: 1/ON)")
    print(f"  Index 4: {outlets_str[4]} → Physical 1 (expected: 1/ON)")
    matches_h2 = outlets_str[0] == "1" and outlets_str[4] == "1"
    if matches_h2:
        print_success("✓ This hypothesis MATCHES!")
    else:
        print_error("✗ This hypothesis does NOT match")

    print()

    # Show actual state
    print(f"{Colors.BOLD}Actual outlet string:{Colors.END} {outlets_str}")
    print(f"  Binary representation: {outlets_str}")
    print()
    print("Based on this data, we can determine the correct mapping.")


async def main() -> int:
    """Main test function."""
    print_header("NetCommander NP-0501DU Physical Device Discovery")
    print_info(f"Host: {HOST}")
    print_info(f"User: {USER}")
    print_info(f"Mode: READ ONLY (no state changes will be made)")
    print()

    auth = aiohttp.BasicAuth(USER, PASSWORD)
    async with aiohttp.ClientSession(auth=auth) as session:
        # Test connection
        if not await test_connection(session):
            print_error("\nConnection test failed. Please check:")
            print("  1. Device IP address is correct")
            print("  2. Device is powered on and accessible")
            print("  3. Credentials are correct in .env file")
            return 1

        # Get and analyze status
        status = await get_status(session)
        if not status:
            return 1

        parsed = parse_status(status)

        # Verify physical state
        await verify_physical_state(session)

        # Discover other endpoints
        await test_all_status_endpoints(session)

        print_header("Test Complete")
        print_success("All read-only tests completed successfully!")
        print()
        print_info("Next steps:")
        print("  1. Review the mapping analysis above")
        print("  2. Confirm which hypothesis matches reality")
        print("  3. Run the interactive toggle test to verify control commands")

        return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
