#!/usr/bin/env python3
"""
Test the rly command format discovered by the user
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv


async def test_rly_commands():
    """Test the rly=X command format"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Testing rly Commands ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # Get initial status
        print("1. Getting initial status...")
        async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
            initial_status = await resp.text()
            print(f"   Initial status: {initial_status}")
        
        # Test rly commands for each outlet
        print(f"\n2. Testing rly commands...")
        
        # Test outlets 0-4 (0-based like user found)
        for outlet in range(5):
            print(f"\n   Testing outlet {outlet}...")
            
            # Send rly command
            url = f"http://{host}/cmd.cgi?rly={outlet}"
            async with session.get(url) as resp:
                result = await resp.text()
                print(f"   rly={outlet} response: {result}")
                
                if "$A0" in result:
                    print("   ✅ SUCCESS!")
                    
                    # Check status after command
                    await asyncio.sleep(0.5)
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        new_status = await resp.text()
                        print(f"   Status after: {new_status}")
                        
                        # Parse outlet states
                        if "$A0," in new_status:
                            outlets = new_status.split(',')[1]
                            print(f"   Outlet states: {outlets}")
                            
                            # Show which outlets changed
                            if "$A0," in initial_status:
                                old_outlets = initial_status.split(',')[1]
                                if outlets != old_outlets:
                                    print(f"   🔄 CHANGED: {old_outlets} -> {outlets}")
                                    
                                    # Update for next comparison
                                    initial_status = new_status
                else:
                    print(f"   ❌ Failed: {result}")
        
        # Test if there are more outlets (some devices have 8)
        print(f"\n3. Testing extended outlet range...")
        for outlet in range(5, 10):
            url = f"http://{host}/cmd.cgi?rly={outlet}"
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result:
                    print(f"   rly={outlet}: ✅ SUCCESS - {result}")
                elif result.strip() != "$AF":
                    print(f"   rly={outlet}: {result}")
        
        # Test if rly toggles or if we need separate on/off
        print(f"\n4. Testing if rly toggles outlets...")
        
        # Test rly=0 twice to see if it toggles
        print("   Double-testing rly=0...")
        for i in range(2):
            url = f"http://{host}/cmd.cgi?rly=0"
            async with session.get(url) as resp:
                result = await resp.text()
                print(f"   Attempt {i+1}: {result}")
                
                await asyncio.sleep(0.5)
                async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                    status = await resp.text()
                    if "$A0," in status:
                        outlets = status.split(',')[1]
                        print(f"   Outlets: {outlets}")
        
        # Test possible on/off commands
        print(f"\n5. Testing explicit on/off commands...")
        
        possible_commands = [
            "rly=0&on=1",
            "rly=0&off=1", 
            "rly=0&state=1",
            "rly=0&state=0",
            "rlyOn=0",
            "rlyOff=0",
            "relay0=1",
            "relay0=0",
        ]
        
        for cmd in possible_commands:
            url = f"http://{host}/cmd.cgi?{cmd}"
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result:
                    print(f"   {cmd}: ✅ SUCCESS - {result}")
                    
                    # Check status
                    await asyncio.sleep(0.3)
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        status = await resp.text()
                        if "$A0," in status:
                            outlets = status.split(',')[1]
                            print(f"   Status: {outlets}")
        
        # Final status
        print(f"\n6. Final status...")
        async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
            final_status = await resp.text()
            print(f"   {final_status}")


if __name__ == "__main__":
    asyncio.run(test_rly_commands())