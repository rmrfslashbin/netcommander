#!/usr/bin/env python3
"""
Check the outlet control page
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup


async def check_outlet_page():
    """Check the outlet control page"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Checking Outlet Control Page ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # Check the outlet setup page
        print("1. Fetching /pwr.htm...")
        async with session.get(f"http://{host}/pwr.htm") as resp:
            if resp.status == 200:
                html = await resp.text()
                print(f"   Page size: {len(html)} bytes")
                
                # Save for inspection
                with open('pwr_page.html', 'w') as f:
                    f.write(html)
                print("   Saved to pwr_page.html")
                
                # Parse for control mechanisms
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for outlet controls
                print("\n   Analyzing outlet controls...")
                
                # Find all links with outlet commands
                links = soup.find_all('a')
                cmd_links = []
                for link in links:
                    href = link.get('href', '')
                    if 'cmd.cgi' in href and '$A' in href:
                        cmd_links.append((link.get_text(strip=True), href))
                
                print(f"   Found {len(cmd_links)} command links:")
                for text, href in cmd_links[:10]:  # First 10
                    print(f"     {text}: {href}")
                
                # Look for JavaScript functions
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('$A3' in script.string or 'outlet' in script.string.lower()):
                        print(f"\n   Found relevant JavaScript:")
                        print(f"     {script.string[:200]}...")
                
                # Try executing one of the found commands
                if cmd_links:
                    print(f"\n2. Testing found command links...")
                    for text, href in cmd_links[:3]:  # Test first 3
                        if '$A3' in href:  # Focus on outlet control
                            print(f"\n   Testing: {text} -> {href}")
                            try:
                                full_url = f"http://{host}{href}" if href.startswith('/') else href
                                async with session.get(full_url) as resp:
                                    result = await resp.text()
                                    print(f"   Response: {result}")
                                    if "$A0" in result:
                                        print("   ✅ SUCCESS! This command works!")
                            except Exception as e:
                                print(f"   Error: {e}")
                
        # Also check other potential pages
        print("\n3. Checking other potential control pages...")
        pages = ['/pwr.htm', '/power.htm', '/outlet.htm', '/relay.htm']
        for page in pages:
            try:
                async with session.get(f"http://{host}{page}") as resp:
                    if resp.status == 200:
                        print(f"   ✅ Found: {page}")
            except:
                pass


if __name__ == "__main__":
    asyncio.run(check_outlet_page())