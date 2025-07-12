#!/usr/bin/env python3
"""
Check the main status/control page
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup


async def check_main_page():
    """Check the main status page for controls"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Checking Main Status Page ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # Check the main status page
        print("1. Fetching /index.htm...")
        async with session.get(f"http://{host}/index.htm") as resp:
            if resp.status == 200:
                html = await resp.text()
                print(f"   Page size: {len(html)} bytes")
                
                # Save for inspection
                with open('index_page.html', 'w') as f:
                    f.write(html)
                print("   Saved to index_page.html")
                
                # Parse for control mechanisms
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for outlet controls
                print("\n   Looking for control buttons/links...")
                
                # Find all links
                links = soup.find_all('a')
                control_links = []
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if ('ON' in text.upper() or 'OFF' in text.upper() or 
                        'REBOOT' in text.upper() or '$A' in href):
                        control_links.append((text, href))
                
                print(f"   Found {len(control_links)} potential control links:")
                for text, href in control_links:
                    print(f"     '{text}' -> {href}")
                
                # Look for buttons
                buttons = soup.find_all(['input', 'button'])
                control_buttons = []
                for button in buttons:
                    btn_type = button.get('type', '')
                    value = button.get('value', '')
                    onclick = button.get('onclick', '')
                    if ('button' in btn_type.lower() or 'submit' in btn_type.lower() or
                        'ON' in value.upper() or 'OFF' in value.upper() or
                        '$A' in onclick):
                        control_buttons.append((btn_type, value, onclick))
                
                print(f"\n   Found {len(control_buttons)} potential control buttons:")
                for btn_type, value, onclick in control_buttons:
                    print(f"     Type: {btn_type}, Value: '{value}', OnClick: {onclick}")
                
                # Look for JavaScript
                scripts = soup.find_all('script')
                print(f"\n   Checking {len(scripts)} scripts for control functions...")
                for script in scripts:
                    if script.string:
                        if '$A3' in script.string or 'outlet' in script.string.lower():
                            print(f"   Found control JavaScript:")
                            print(f"     {script.string[:300]}...")
                
                # Test any found control links
                if control_links:
                    print(f"\n2. Testing control links...")
                    for text, href in control_links[:3]:  # Test first 3
                        if href and href != '#':
                            print(f"\n   Testing: {text} -> {href}")
                            try:
                                if href.startswith('/'):
                                    full_url = f"http://{host}{href}"
                                elif href.startswith('http'):
                                    full_url = href
                                else:
                                    full_url = f"http://{host}/{href}"
                                
                                async with session.get(full_url) as resp:
                                    result = await resp.text()
                                    print(f"   Response: {result[:100]}...")
                                    if "$A0" in result:
                                        print("   ✅ SUCCESS!")
                                    elif "$AF" in result:
                                        print("   ❌ Failed - device returned error")
                            except Exception as e:
                                print(f"   Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_main_page())