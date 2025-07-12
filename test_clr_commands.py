#!/usr/bin/env python3
"""
Test the clrR commands found in the web interface
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv


async def test_clr_commands():
    """Test the clrR commands"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Testing clrR Commands ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # Get initial status
        print("1. Getting initial status...")
        async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
            initial_status = await resp.text()
            print(f"   Initial status: {initial_status}")
        
        # Test the clrR commands found in the interface
        clr_commands = [1, 2, 3, 4, 5, 6]
        
        print(f"\n2. Testing clrR commands...")
        for cmd_id in clr_commands:
            print(f"\n   Testing clrR={cmd_id}...")
            
            # Send command
            url = f"http://{host}/cmd.cgi?clrR={cmd_id}"
            async with session.get(url) as resp:
                result = await resp.text()
                print(f"   Response: {result}")
                
                # Check if successful
                if "$A0" in result:
                    print("   ✅ SUCCESS!")
                elif "$AF" in result:
                    print("   ❌ Failed")
                elif result.strip() == "":
                    print("   Empty response - might be success")
                
                # Check status after command
                await asyncio.sleep(0.5)
                async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                    new_status = await resp.text()
                    print(f"   Status after: {new_status}")
                    
                    # Compare with initial
                    if new_status != initial_status:
                        print("   🔄 STATUS CHANGED!")
                        initial_status = new_status  # Update for next comparison
                
        # Test if these might be toggle commands
        print(f"\n3. Testing if commands toggle outlets...")
        
        # Test clrR=1 twice to see if it toggles
        print(f"\n   Double-testing clrR=1...")
        for i in range(2):
            url = f"http://{host}/cmd.cgi?clrR=1"
            async with session.get(url) as resp:
                result = await resp.text()
                print(f"   Attempt {i+1}: {result}")
                
                await asyncio.sleep(0.5)
                async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                    status = await resp.text()
                    print(f"   Status: {status}")
        
        # Test other possible command formats
        print(f"\n4. Testing other possible command formats...")
        
        other_commands = [
            "setR=1",       # Set relay
            "togR=1",       # Toggle relay
            "pwrR=1",       # Power relay
            "outR=1",       # Outlet relay
            "rel1=1",       # Relay 1
            "outlet1=1",    # Outlet 1
        ]
        
        for cmd in other_commands:
            url = f"http://{host}/cmd.cgi?{cmd}"
            print(f"\n   Testing: {cmd}")
            async with session.get(url) as resp:
                result = await resp.text()
                print(f"   Response: {result}")
                if "$A0" in result or (result.strip() != "" and "$AF" not in result):
                    print("   Might work! Checking status...")
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        status = await resp.text()
                        print(f"   Status: {status}")


if __name__ == "__main__":
    asyncio.run(test_clr_commands())