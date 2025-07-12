#!/usr/bin/env python3
"""
Test more command variations to find outlet ON/OFF controls
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv


async def test_more_commands():
    """Test various command patterns"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Testing More Command Patterns ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # Test different command patterns based on clrR success
        print("1. Testing 'setR' patterns (since clrR works)...")
        
        # If clrR works, maybe setR works too
        set_commands = []
        for outlet in range(1, 7):  # Test outlets 1-6
            for state in [0, 1]:   # OFF, ON
                set_commands.append(f"setR={outlet}&state={state}")
                set_commands.append(f"setR={outlet},{state}")
                set_commands.append(f"setR{outlet}={state}")
        
        for cmd in set_commands[:10]:  # Test first 10 to avoid spam
            url = f"http://{host}/cmd.cgi?{cmd}"
            print(f"\n   Testing: {cmd}")
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result:
                    print(f"   ✅ SUCCESS: {result}")
                    # Check status
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        status = await resp.text()
                        print(f"   Status: {status}")
                elif result.strip() != "$AF":
                    print(f"   Interesting: {result}")
        
        print("\n2. Testing relay patterns...")
        
        # Try relay-based commands
        relay_commands = []
        for outlet in range(1, 6):  # 5 outlets
            relay_commands.extend([
                f"R{outlet}=0",
                f"R{outlet}=1", 
                f"r{outlet}=0",
                f"r{outlet}=1",
                f"relay{outlet}=0",
                f"relay{outlet}=1",
            ])
        
        for cmd in relay_commands[:12]:  # Test first 12
            url = f"http://{host}/cmd.cgi?{cmd}"
            print(f"\n   Testing: {cmd}")
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result:
                    print(f"   ✅ SUCCESS: {result}")
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        status = await resp.text()
                        print(f"   Status: {status}")
        
        print("\n3. Testing outlet patterns...")
        
        # Try outlet-based commands  
        outlet_commands = []
        for outlet in range(1, 6):  # 5 outlets
            outlet_commands.extend([
                f"O{outlet}=0",
                f"O{outlet}=1",
                f"o{outlet}=0", 
                f"o{outlet}=1",
                f"out{outlet}=0",
                f"out{outlet}=1",
            ])
        
        for cmd in outlet_commands[:12]:  # Test first 12
            url = f"http://{host}/cmd.cgi?{cmd}"
            print(f"\n   Testing: {cmd}")
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result:
                    print(f"   ✅ SUCCESS: {result}")
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        status = await resp.text()
                        print(f"   Status: {status}")
        
        print("\n4. Testing if clrR might be state-dependent...")
        
        # Maybe clrR only works when outlets are ON, try the opposite
        opposite_commands = []
        for outlet in range(1, 6):
            opposite_commands.extend([
                f"setR={outlet}",    # Set without state
                f"onR={outlet}",     # Turn on
                f"offR={outlet}",    # Turn off
                f"pwrR={outlet}",    # Power command
            ])
        
        for cmd in opposite_commands:
            url = f"http://{host}/cmd.cgi?{cmd}"
            print(f"\n   Testing: {cmd}")
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result:
                    print(f"   ✅ SUCCESS: {result}")
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        status = await resp.text()
                        print(f"   Status: {status}")
                        
        print("\n5. Final test - check if any outlets actually changed...")
        
        # Get final status and compare
        async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
            final_status = await resp.text()
            print(f"   Final status: {final_status}")


if __name__ == "__main__":
    asyncio.run(test_more_commands())