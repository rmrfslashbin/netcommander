#!/usr/bin/env python3
"""
Test the complete range of clrR commands and look for actual control buttons
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv


async def test_final_commands():
    """Test extended clrR range and check for actual control interface"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    print("=== Testing Final Command Set ===\n")
    
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        
        # Test extended clrR range (found 10, 11 in JS)
        print("1. Testing extended clrR range...")
        
        # Get initial status
        async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
            initial_status = await resp.text()
            print(f"   Initial status: {initial_status}")
        
        # Test clrR from 1-20
        for cmd_id in range(1, 21):
            url = f"http://{host}/cmd.cgi?clrR={cmd_id}"
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result:
                    print(f"   clrR={cmd_id}: ✅ SUCCESS")
                    
                    # Check if status changed
                    await asyncio.sleep(0.3)
                    async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
                        new_status = await resp.text()
                        if new_status != initial_status:
                            print(f"   STATUS CHANGED! {initial_status} -> {new_status}")
                            initial_status = new_status
                elif result.strip() == "":
                    print(f"   clrR={cmd_id}: Empty response")
                elif "$AF" not in result:
                    print(f"   clrR={cmd_id}: Unexpected: {result}")
        
        print(f"\n2. Checking if web control is actually locked...")
        
        # Check the administration page that might have unlock settings
        async with session.get(f"http://{host}/adm.htm") as resp:
            if resp.status == 200:
                html = await resp.text()
                if 'lock' in html.lower() or 'enable' in html.lower():
                    print("   Found admin page with potential lock settings")
                    
                    # Save for inspection
                    with open('admin_page.html', 'w') as f:
                        f.write(html)
                    print("   Saved to admin_page.html")
                    
                    # Look for lock checkboxes
                    import re
                    lock_patterns = re.findall(r'name="[^"]*[Ll]ock?[^"]*"', html)
                    enable_patterns = re.findall(r'name="[^"]*[Ee]nab[^"]*"', html)
                    
                    print(f"   Found lock controls: {lock_patterns}")
                    print(f"   Found enable controls: {enable_patterns}")
        
        print(f"\n3. Testing direct outlet status commands...")
        
        # Try to get individual outlet status  
        for outlet in range(1, 6):
            url = f"http://{host}/cmd.cgi?$A5,{outlet}"
            async with session.get(url) as resp:
                result = await resp.text()
                if "$A0" in result and result != initial_status:
                    print(f"   Outlet {outlet} status: {result}")
        
        print(f"\n4. Final attempt - testing if outlets are physically controllable...")
        
        # Based on what we know about locked devices, maybe we need to:
        # 1. Clear all errors first
        # 2. Then try control
        
        print("   Clearing all possible error states...")
        for clear_id in [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15]:
            url = f"http://{host}/cmd.cgi?clrR={clear_id}"
            async with session.get(url) as resp:
                await resp.text()  # Don't spam output
        
        print("   Attempting control after clearing...")
        
        # Try the standard $A3 again
        async with session.get(f"http://{host}/cmd.cgi?$A3,1,0") as resp:
            result = await resp.text()
            print(f"   $A3,1,0 result: {result}")
            
        # Get final status
        async with session.get(f"http://{host}/cmd.cgi?$A5") as resp:
            final_status = await resp.text()
            print(f"   Final status: {final_status}")
            
        # Final verdict
        if final_status == initial_status:
            print(f"\n❌ CONCLUSION: Device appears to have web control locked")
            print(f"   All outlets remain in the same state despite successful command execution")
            print(f"   This is likely configured in the device settings")
        else:
            print(f"\n✅ CONCLUSION: Control commands are working!")


if __name__ == "__main__":
    asyncio.run(test_final_commands())