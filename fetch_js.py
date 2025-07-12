#!/usr/bin/env python3
"""
Fetch JavaScript files to understand control mechanism
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv


async def fetch_js_files():
    """Fetch JavaScript files from the device"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Fetching JavaScript Files ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # JavaScript files referenced in the HTML
        js_files = ['/syn.js', '/syn1.js']
        
        for js_file in js_files:
            print(f"Fetching {js_file}...")
            async with session.get(f"http://{host}{js_file}") as resp:
                if resp.status == 200:
                    content = await resp.text()
                    print(f"   Size: {len(content)} bytes")
                    
                    # Save to file
                    filename = js_file.replace('/', '') 
                    with open(filename, 'w') as f:
                        f.write(content)
                    print(f"   Saved to {filename}")
                    
                    # Look for control functions
                    if 'clrR' in content or '$A' in content or 'outlet' in content.lower():
                        print(f"   Contains control references!")
                        
                        # Extract relevant functions
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if ('clrR' in line or '$A' in line or 
                                'outlet' in line.lower() or 'relay' in line.lower()):
                                print(f"   Line {i+1}: {line.strip()}")
                                
                                # Show surrounding context
                                start = max(0, i-2)
                                end = min(len(lines), i+3)
                                if start != i or end != i+1:
                                    print(f"   Context:")
                                    for j in range(start, end):
                                        marker = ">>>" if j == i else "   "
                                        print(f"   {marker} {j+1}: {lines[j].strip()}")
                                    print()
                    
                else:
                    print(f"   Failed to fetch: {resp.status}")


if __name__ == "__main__":
    asyncio.run(fetch_js_files())