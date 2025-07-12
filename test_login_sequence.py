#!/usr/bin/env python3
"""
Test if device requires explicit login command even with Basic Auth
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv


async def test_login_sequence():
    """Test login sequence with commands"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    base_url = f"http://{host}"
    auth = aiohttp.BasicAuth(username, password)
    
    async with aiohttp.ClientSession(auth=auth) as session:
        print("=== Testing Login Sequence ===\n")
        
        # Test 1: Try $A1 login command with Basic Auth
        print("1. Sending $A1 login command...")
        url = f"{base_url}/cmd.cgi?$A1,{username},{password}"
        async with session.get(url) as resp:
            text = await resp.text()
            print(f"   Response: {text}")
            
        # Test 2: Try status after login
        print("\n2. Getting status after login...")
        async with session.get(f"{base_url}/cmd.cgi?$A5") as resp:
            text = await resp.text()
            print(f"   Response: {text}")
            
        # Test 3: Try outlet control after login
        print("\n3. Attempting outlet control after login...")
        async with session.get(f"{base_url}/cmd.cgi?$A3,1,0") as resp:
            text = await resp.text()
            print(f"   Response: {text}")
            
        # Test 4: Try logout and then control
        print("\n4. Testing logout ($A2)...")
        async with session.get(f"{base_url}/cmd.cgi?$A2") as resp:
            text = await resp.text()
            print(f"   Response: {text}")
            
        # Test 5: Try control after logout
        print("\n5. Attempting control after logout...")
        async with session.get(f"{base_url}/cmd.cgi?$A3,1,0") as resp:
            text = await resp.text()
            print(f"   Response: {text}")
            
        # Test 6: Check if we need channel selection
        print("\n6. Testing channel selection...")
        async with session.get(f"{base_url}/cmd.cgi?/sset,1") as resp:
            text = await resp.text()
            print(f"   Response: {text}")
            
        # Test 7: List all commands ($A0 might show help)
        print("\n7. Testing help/list commands...")
        test_cmds = ["$A0", "$AA", "$AH", "?", "help"]
        for cmd in test_cmds:
            async with session.get(f"{base_url}/cmd.cgi?{cmd}") as resp:
                text = await resp.text()
                if text and text != "$AF":
                    print(f"   {cmd}: {text[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_login_sequence())