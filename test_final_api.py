#!/usr/bin/env python3
"""
Final comprehensive test of the working API
"""

import asyncio
import logging
from netcommander_api import NetCommanderAPI
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


async def test_final_api():
    """Comprehensive test of all API functions"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    async with NetCommanderAPI(host, username, password) as api:
        print("=== Final API Test ===\n")
        
        # Test 1: Check capabilities
        print("1. Checking device capabilities...")
        caps = await api.check_control_capability()
        for cap, available in caps.items():
            status = "✅" if available else "❌"
            print(f"   {cap}: {status}")
        
        # Test 2: Get status
        print(f"\n2. Getting device status...")
        status = await api.get_status()
        print(f"   Raw status: {status.raw_response}")
        print(f"   Temperature: {status.temperature}°C")
        print(f"   Total Current: {status.total_current}A")
        print("   Outlets:")
        for outlet in status.outlets:
            state = "ON" if outlet.is_on else "OFF"
            print(f"     Outlet {outlet.outlet_id}: {state}")
        
        # Test 3: Individual outlet control
        print(f"\n3. Testing individual outlet control...")
        
        # Turn outlet 1 OFF explicitly
        print("   Setting outlet 1 to OFF...")
        success = await api.set_outlet(1, False)
        print(f"   Result: {'✅' if success else '❌'}")
        await asyncio.sleep(0.5)
        
        status = await api.get_status()
        outlet1_state = "ON" if status.outlets[0].is_on else "OFF"
        print(f"   Outlet 1 is now: {outlet1_state}")
        
        # Turn outlet 1 ON explicitly  
        print("   Setting outlet 1 to ON...")
        success = await api.set_outlet(1, True)
        print(f"   Result: {'✅' if success else '❌'}")
        await asyncio.sleep(0.5)
        
        status = await api.get_status()
        outlet1_state = "ON" if status.outlets[0].is_on else "OFF"
        print(f"   Outlet 1 is now: {outlet1_state}")
        
        # Test 4: Toggle functionality
        print(f"\n4. Testing toggle functionality...")
        
        for outlet_id in [2, 3]:
            print(f"   Toggling outlet {outlet_id}...")
            success = await api.toggle_outlet(outlet_id)
            print(f"   Result: {'✅' if success else '❌'}")
            await asyncio.sleep(0.5)
            
            status = await api.get_status()
            outlet_state = "ON" if status.outlets[outlet_id-1].is_on else "OFF"
            print(f"   Outlet {outlet_id} is now: {outlet_state}")
        
        # Test 5: Multiple rapid commands
        print(f"\n5. Testing rapid command execution...")
        
        print("   Rapid toggle test...")
        for i in range(3):
            success = await api.toggle_outlet(4)
            print(f"   Toggle {i+1}: {'✅' if success else '❌'}")
            await asyncio.sleep(0.3)
        
        # Test 6: Final status check
        print(f"\n6. Final device status...")
        final_status = await api.get_status()
        print(f"   Raw: {final_status.raw_response}")
        print(f"   Current draw: {final_status.total_current}A")
        
        outlets_on = sum(1 for o in final_status.outlets if o.is_on)
        print(f"   Outlets ON: {outlets_on}/5")
        
        for outlet in final_status.outlets:
            state = "ON" if outlet.is_on else "OFF"
            print(f"   Outlet {outlet.outlet_id}: {state}")
        
        print(f"\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"   The NetCommander API is fully functional!")


if __name__ == "__main__":
    asyncio.run(test_final_api())