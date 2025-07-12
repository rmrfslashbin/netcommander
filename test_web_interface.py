#!/usr/bin/env python3
"""
Explore the web interface to understand control mechanism
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup


async def explore_web_interface():
    """Fetch and analyze the web interface"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Exploring NetCommander Web Interface ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # Get the main page
        print("1. Fetching main page...")
        async with session.get(f"http://{host}/") as resp:
            if resp.status == 200:
                html = await resp.text()
                print(f"   Page size: {len(html)} bytes")
                
                # Parse HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for forms
                forms = soup.find_all('form')
                print(f"   Found {len(forms)} forms")
                
                for i, form in enumerate(forms):
                    print(f"\n   Form {i+1}:")
                    print(f"     Action: {form.get('action', 'none')}")
                    print(f"     Method: {form.get('method', 'none')}")
                    
                    # Find inputs
                    inputs = form.find_all(['input', 'select', 'button'])
                    for inp in inputs:
                        print(f"     Input: name='{inp.get('name')}' type='{inp.get('type')}' value='{inp.get('value')}'")
                
                # Look for links with outlet control
                links = soup.find_all('a')
                control_links = [link for link in links if 'outlet' in str(link).lower() or '$A' in str(link)]
                
                print(f"\n   Found {len(control_links)} potential control links")
                for link in control_links[:5]:  # First 5
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    print(f"     Link: {text} -> {href}")
                
                # Look for JavaScript
                scripts = soup.find_all('script')
                print(f"\n   Found {len(scripts)} script tags")
                
                # Check for frames
                frames = soup.find_all(['frame', 'iframe'])
                if frames:
                    print(f"\n   Found {len(frames)} frames")
                    for frame in frames:
                        print(f"     Frame: {frame.get('src', 'no src')}")
                
                # Save HTML for manual inspection
                with open('main_page.html', 'w') as f:
                    f.write(html)
                print("\n   Saved HTML to main_page.html for inspection")
                
        # Try common control pages
        print("\n2. Checking common control pages...")
        pages = [
            '/index.html',
            '/control.html',
            '/outlets.html',
            '/power.html',
            '/switch.html',
            '/main.html',
            '/home.html'
        ]
        
        for page in pages:
            url = f"http://{host}{page}"
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        print(f"   ✅ Found: {page}")
                        # Check if it has outlet controls
                        text = await resp.text()
                        if 'outlet' in text.lower() or '$A3' in text:
                            print(f"      Contains outlet references!")
            except:
                pass
        
        # Check the actual user - case might matter
        print("\n3. Testing username variations...")
        for test_user in ['admin', 'Admin', 'ADMIN', username]:
            # Try status with each username variation
            test_auth = aiohttp.BasicAuth(test_user, password)
            async with aiohttp.ClientSession(auth=test_auth) as test_session:
                try:
                    async with test_session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            print(f"   {test_user}: Status works - {text[:20]}...")
                            
                            # Try control
                            async with test_session.get(f"http://{host}/cmd.cgi?$A3,1,0") as resp2:
                                text2 = await resp2.text()
                                if "$A0" in text2:
                                    print(f"   ✅ CONTROL WORKS with username: {test_user}")
                                else:
                                    print(f"   Control failed: {text2}")
                except:
                    print(f"   {test_user}: Failed")


if __name__ == "__main__":
    # Install beautifulsoup4 if needed
    try:
        import bs4
    except ImportError:
        print("Installing beautifulsoup4...")
        import subprocess
        subprocess.check_call(["uv", "pip", "install", "beautifulsoup4"])
    
    asyncio.run(explore_web_interface())