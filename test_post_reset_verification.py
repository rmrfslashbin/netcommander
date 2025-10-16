#!/usr/bin/env python3
"""
Post-Reset Verification Test

Now that the device has been factory reset and appears to be working,
let's verify the correct behavior and document it.
"""

import asyncio
import os
import sys
import json
from datetime import datetime
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# Device should be at default IP after reset
HOST = os.getenv("NETCOMMANDER_HOST", "192.168.1.100")
USER = "admin"  # Default after reset
PASSWORD = "admin"  # Default after reset


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def get_status(session: aiohttp.ClientSession) -> str:
    """Get device status."""
    url = f"http://{HOST}/cmd.cgi?$A5"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def send_explicit_on(session: aiohttp.ClientSession, port: int) -> str:
    """Send explicit ON command."""
    url = f"http://{HOST}/cmd.cgi?$A3,{port},1"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def send_explicit_off(session: aiohttp.ClientSession, port: int) -> str:
    """Send explicit OFF command."""
    url = f"http://{HOST}/cmd.cgi?$A3,{port},0"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def toggle_outlet(session: aiohttp.ClientSession, rly: int) -> str:
    """Send toggle command."""
    url = f"http://{HOST}/cmd.cgi?rly={rly}"
    async with session.get(url) as resp:
        return (await resp.text()).strip()


async def main() -> int:
    """Main verification test."""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("="*80)
    print(" Post-Reset Verification Test ".center(80))
    print("="*80)
    print(Colors.END)

    print(f"\n{Colors.GREEN}✓ Device has been factory reset{Colors.END}")
    print(f"{Colors.GREEN}✓ Device appears to be working correctly{Colors.END}\n")

    print(f"{Colors.CYAN}This test will verify:{Colors.END}")
    print("  1. All outlets start in OFF state")
    print("  2. Explicit commands ($A3) work (no $AF errors)")
    print("  3. Status matches reality (no inverted logic)")
    print("  4. LEDs match power state")
    print("  5. Complete mapping is correct")
    print()

    auth = aiohttp.BasicAuth(USER, PASSWORD)
    results = {
        "timestamp": datetime.now().isoformat(),
        "device_ip": HOST,
        "reset_successful": True,
        "tests": []
    }

    async with aiohttp.ClientSession(auth=auth) as session:
        # Test 1: Initial state
        print(f"{Colors.BOLD}Test 1: Initial State (all OFF after reset){Colors.END}")
        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""
        current = parts[2] if len(parts) > 2 else ""

        print(f"Status: {status}")
        print(f"Outlets: {outlets}")
        print(f"Current: {current}A")

        if outlets == "00000":
            print(f"{Colors.GREEN}✓ All outlets report OFF{Colors.END}")
            results["tests"].append({"test": "initial_state", "status": "PASS"})
        else:
            print(f"{Colors.RED}✗ Unexpected initial state: {outlets}{Colors.END}")
            results["tests"].append({"test": "initial_state", "status": "FAIL", "value": outlets})

        # Test 2: Explicit ON command
        print(f"\n{Colors.BOLD}Test 2: Explicit ON Command ($A3,1,1){Colors.END}")
        response = await send_explicit_on(session, 1)
        print(f"Response: {response}")

        if response.startswith("$A0"):
            print(f"{Colors.GREEN}✓ Command accepted (returned $A0){Colors.END}")
            results["tests"].append({"test": "explicit_on", "status": "PASS"})
        else:
            print(f"{Colors.RED}✗ Command failed (returned {response}){Colors.END}")
            results["tests"].append({"test": "explicit_on", "status": "FAIL", "response": response})
            print(f"\n{Colors.RED}CRITICAL: Device still rejecting explicit commands!{Colors.END}")
            return 1

        await asyncio.sleep(1)

        # Test 3: Verify status matches
        print(f"\n{Colors.BOLD}Test 3: Status After Turning ON Outlet 1{Colors.END}")
        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""

        print(f"Status: {status}")
        print(f"Outlets: {outlets}")

        print(f"\n{Colors.YELLOW}Physical verification needed:{Colors.END}")
        led_on = input("  Is outlet 1 LED ON? (y/n): ").strip().lower() == 'y'
        has_power = input("  Does outlet 1 have POWER? (y/n): ").strip().lower() == 'y'

        status_bit = outlets[4] if len(outlets) >= 5 else '?'  # Position 4 = outlet 1

        print(f"\nVerification:")
        print(f"  LED: {'ON' if led_on else 'OFF'}")
        print(f"  Power: {'ON' if has_power else 'OFF'}")
        print(f"  Status bit [4]: {status_bit}")

        if led_on and has_power and status_bit == '1':
            print(f"\n{Colors.GREEN}✓✓✓ PERFECT! All states aligned:{Colors.END}")
            print(f"{Colors.GREEN}  LED=ON, Power=ON, Status=1{Colors.END}")
            print(f"{Colors.GREEN}  NO INVERTED LOGIC!{Colors.END}")
            results["tests"].append({"test": "state_alignment", "status": "PASS"})
        else:
            print(f"\n{Colors.RED}✗ States don't match!{Colors.END}")
            print(f"  Expected: LED=ON, Power=ON, Status=1")
            print(f"  Got: LED={'ON' if led_on else 'OFF'}, Power={'ON' if has_power else 'OFF'}, Status={status_bit}")
            results["tests"].append({
                "test": "state_alignment",
                "status": "FAIL",
                "led": led_on,
                "power": has_power,
                "status_bit": status_bit
            })

        # Test 4: Explicit OFF command
        print(f"\n{Colors.BOLD}Test 4: Explicit OFF Command ($A3,1,0){Colors.END}")
        response = await send_explicit_off(session, 1)
        print(f"Response: {response}")

        if response.startswith("$A0"):
            print(f"{Colors.GREEN}✓ Command accepted{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Command failed: {response}{Colors.END}")

        await asyncio.sleep(1)

        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""

        print(f"Status after OFF: {outlets}")

        led_on = input("  Is outlet 1 LED OFF now? (y/n): ").strip().lower() != 'y'  # Asking if OFF
        has_power = input("  Does outlet 1 have NO power? (y/n): ").strip().lower() != 'y'  # Asking if no power

        status_bit = outlets[4] if len(outlets) >= 5 else '?'

        if not led_on and not has_power and status_bit == '0':
            print(f"{Colors.GREEN}✓ All states aligned (OFF){Colors.END}")
            results["tests"].append({"test": "explicit_off", "status": "PASS"})
        else:
            print(f"{Colors.RED}✗ States don't match after OFF{Colors.END}")
            results["tests"].append({"test": "explicit_off", "status": "FAIL"})

        # Test 5: Quick mapping verification
        print(f"\n{Colors.BOLD}Test 5: Quick Mapping Verification{Colors.END}")
        print("Testing outlet 5 to verify reverse mapping...")

        response = await send_explicit_on(session, 5)
        await asyncio.sleep(1)
        status = await get_status(session)
        parts = status.split(",")
        outlets = parts[1] if len(parts) > 1 else ""

        print(f"Status after turning ON outlet 5: {outlets}")
        print(f"Expected: 10000 (leftmost bit = outlet 5)")

        if outlets == "10000":
            print(f"{Colors.GREEN}✓ Mapping correct (outlet 5 → position 0){Colors.END}")
            results["tests"].append({"test": "mapping_verification", "status": "PASS"})
        else:
            print(f"{Colors.YELLOW}? Unexpected: {outlets}{Colors.END}")
            results["tests"].append({"test": "mapping_verification", "status": "UNEXPECTED", "value": outlets})

        # Turn off outlet 5
        await send_explicit_off(session, 5)

        # Summary
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("="*80)
        print(" Test Summary ".center(80))
        print("="*80)
        print(Colors.END)

        all_passed = all(t.get("status") == "PASS" for t in results["tests"])

        if all_passed:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓✓✓ ALL TESTS PASSED ✓✓✓{Colors.END}")
            print(f"\n{Colors.GREEN}Device is working correctly!{Colors.END}")
            print(f"{Colors.GREEN}  • No inverted logic{Colors.END}")
            print(f"{Colors.GREEN}  • Explicit commands work{Colors.END}")
            print(f"{Colors.GREEN}  • Status matches reality{Colors.END}")
            print(f"{Colors.GREEN}  • Ready for integration development{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}Some tests had issues - review above{Colors.END}")

        # Save results
        filename = f"post_reset_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n{Colors.CYAN}Results saved to: {filename}{Colors.END}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted{Colors.END}")
        sys.exit(130)
