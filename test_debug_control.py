#!/usr/bin/env python3
"""
Debug control issues - test different approaches
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv


async def debug_control():
    """Try various control approaches"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Debugging NetCommander Control ===\n")
    
    # Test 1: Check if we need to select a bank/channel first
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        print("1. Testing bank/channel selection commands...")
        test_commands = [
            "/bsel,1",      # Bank select
            "/ssel,1",      # Channel select  
            "/sset,1",      # Set select
            "$AB,1",        # Possible bank command
            "$AC,1",        # Possible channel command
        ]
        
        for cmd in test_commands:
            url = f"http://{host}/cmd.cgi?{cmd}"
            print(f"\n   Testing: {cmd}")
            async with session.get(url) as resp:
                text = await resp.text()
                print(f"   Response: {text}")
                
                # If successful, try control
                if "$A0" in text:
                    print("   Success! Testing outlet control...")
                    async with session.get(f"http://{host}/cmd.cgi?$A3,1,0") as resp2:
                        text2 = await resp2.text()
                        print(f"   Control response: {text2}")
        
        print("\n2. Testing different outlet numbering...")
        # Some devices use 0-based, some 1-based, some need padding
        test_formats = [
            "$A3,0,0",      # 0-based index
            "$A3,1,0",      # 1-based index
            "$A3,01,0",     # Zero-padded
            "$A3,001,0",    # Three digits
            "$A3,A,0",      # Letter-based
            "$A3,a,0",      # Lowercase letter
        ]
        
        for fmt in test_formats:
            url = f"http://{host}/cmd.cgi?{fmt}"
            print(f"\n   Testing: {fmt}")
            async with session.get(url) as resp:
                text = await resp.text()
                print(f"   Response: {text}")
                if "$A0" in text:
                    print("   ✅ SUCCESS! This format works!")
                    break
        
        print("\n3. Testing with explicit login first...")
        # Try explicit login
        login_url = f"http://{host}/cmd.cgi?$A1,{username},{password}"
        print(f"   Login attempt...")
        async with session.get(login_url) as resp:
            text = await resp.text()
            print(f"   Login response: {text}")
            
        # Try control after login
        print("   Control after login...")
        async with session.get(f"http://{host}/cmd.cgi?$A3,1,0") as resp:
            text = await resp.text()
            print(f"   Response: {text}")
        
        print("\n4. Testing raw HTTP without Basic Auth but with login...")
        # Create new session without auth
        async with aiohttp.ClientSession() as raw_session:
            # Try login command
            login_url = f"http://{host}/cmd.cgi?$A1,{username},{password}"
            print("   Raw login...")
            async with raw_session.get(login_url) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    text = await resp.text()
                    print(f"   Response: {text}")
                    
                    # Try control
                    print("   Control after raw login...")
                    async with raw_session.get(f"http://{host}/cmd.cgi?$A3,1,0") as resp2:
                        text2 = await resp2.text()
                        print(f"   Response: {text2}")
        
        print("\n5. Checking for web UI endpoints...")
        # Some devices have separate control endpoints
        endpoints = [
            "/outlet.cgi?outlet=1&state=0",
            "/control.cgi?outlet=1&state=0",
            "/switch.cgi?id=1&state=0",
            "/relay.cgi?relay=1&state=0",
        ]
        
        for endpoint in endpoints:
            url = f"http://{host}{endpoint}"
            print(f"\n   Testing: {endpoint}")
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        print(f"   Response: {text[:100]}...")
                    else:
                        print(f"   Status: {resp.status}")
            except Exception as e:
                print(f"   Error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_control())