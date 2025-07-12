#!/usr/bin/env python3
"""
Detailed API testing to debug outlet control
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from netcommander_api import NetCommanderAPI

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_commands():
    """Test various command formats"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    async with NetCommanderAPI(host, username, password) as api:
        print("=== Testing Command Formats ===\n")
        
        # Test 1: Get current status
        print("1. Getting current status...")
        status = await api.get_status()
        print(f"   Current state: {status.raw_response}")
        outlet1_current = status.outlets[0].is_on
        print(f"   Outlet 1 is: {'ON' if outlet1_current else 'OFF'}\n")
        
        # Test 2: Try to toggle outlet 1
        new_state = not outlet1_current
        print(f"2. Attempting to turn outlet 1 {'OFF' if outlet1_current else 'ON'}...")
        success = await api.set_outlet(1, new_state)
        print(f"   Result: {'SUCCESS' if success else 'FAILED'}\n")
        
        # Test 3: Check status again
        print("3. Checking status after toggle attempt...")
        status2 = await api.get_status()
        print(f"   New state: {status2.raw_response}")
        outlet1_new = status2.outlets[0].is_on
        print(f"   Outlet 1 is now: {'ON' if outlet1_new else 'OFF'}")
        print(f"   State changed: {'YES' if outlet1_new != outlet1_current else 'NO'}\n")
        
        # Test 4: Try manual command variations
        print("4. Testing command variations...")
        
        # Direct command test
        import aiohttp
        auth = aiohttp.BasicAuth(username, password)
        async with aiohttp.ClientSession(auth=auth) as session:
            # Try different command formats
            test_commands = [
                ("$A3,1,0", "Standard format - Turn OFF"),
                ("$A3,1,1", "Standard format - Turn ON"),
                ("$A3,01,0", "Zero-padded outlet - Turn OFF"),
                ("$A3,01,1", "Zero-padded outlet - Turn ON"),
            ]
            
            for cmd, desc in test_commands:
                url = f"http://{host}/cmd.cgi?{cmd}"
                print(f"\n   Testing: {desc}")
                print(f"   URL: {url}")
                
                async with session.get(url) as resp:
                    text = await resp.text()
                    print(f"   Response: {text}")
                    
                    # Check if command affected the state
                    await asyncio.sleep(0.5)  # Brief delay
                    status_check = await api.get_status()
                    print(f"   Status after: {status_check.raw_response}")


if __name__ == "__main__":
    asyncio.run(test_commands())