#!/usr/bin/env python3
"""
Test outlet control with updated permissions
"""

import asyncio
import logging
from netcommander_api import NetCommanderAPI
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


async def test_outlet_control():
    """Test all outlet control capabilities"""
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    async with NetCommanderAPI(host, username, password) as api:
        print("=== NetCommander Control Test ===\n")
        
        # Check capabilities first
        print("1. Checking device capabilities...")
        caps = await api.check_control_capability()
        for cap, available in caps.items():
            status = "✅" if available else "❌"
            print(f"   {cap}: {status}")
        print()
        
        # Get initial status
        print("2. Getting initial status...")
        status = await api.get_status()
        print(f"   Status: {status.raw_response}")
        print(f"   Temperature: {status.temperature}°C")
        print(f"   Total Current: {status.total_current}A")
        print("   Outlets:")
        for outlet in status.outlets:
            state = "ON" if outlet.is_on else "OFF"
            print(f"     Outlet {outlet.outlet_id}: {state}")
        print()
        
        # Test individual outlet control
        print("3. Testing individual outlet control...")
        
        # Turn off outlet 1
        print("   Turning outlet 1 OFF...")
        success = await api.set_outlet(1, False)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        await asyncio.sleep(1)  # Brief delay
        
        # Check status
        status = await api.get_status()
        print(f"   New status: {status.raw_response}")
        
        # Turn on outlet 1
        print("\n   Turning outlet 1 ON...")
        success = await api.set_outlet(1, True)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        await asyncio.sleep(1)
        
        # Test toggling multiple outlets
        print("\n4. Testing multiple outlet control...")
        for outlet_id in [2, 3, 4, 5]:
            print(f"   Toggling outlet {outlet_id}...")
            # Get current state
            status = await api.get_status()
            current_state = status.outlets[outlet_id - 1].is_on
            new_state = not current_state
            
            success = await api.set_outlet(outlet_id, new_state)
            print(f"   Outlet {outlet_id}: {'ON' if new_state else 'OFF'} - {'✅' if success else '❌'}")
            await asyncio.sleep(0.5)
        
        # Test all outlets control
        print("\n5. Testing all outlets control...")
        
        print("   Turning ALL outlets OFF...")
        success = await api.set_all_outlets(False)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        await asyncio.sleep(2)
        status = await api.get_status()
        print(f"   Status: {status.raw_response}")
        
        print("\n   Turning ALL outlets ON...")
        success = await api.set_all_outlets(True)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        await asyncio.sleep(2)
        status = await api.get_status()
        print(f"   Status: {status.raw_response}")
        
        # Test outlet reboot
        print("\n6. Testing outlet reboot (outlet 3)...")
        print("   Rebooting outlet 3...")
        success = await api.reboot_outlet(3)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        # Final status
        print("\n7. Final device status...")
        status = await api.get_status()
        print(f"   Status: {status.raw_response}")
        for outlet in status.outlets:
            state = "ON" if outlet.is_on else "OFF"
            print(f"   Outlet {outlet.outlet_id}: {state}")


if __name__ == "__main__":
    asyncio.run(test_outlet_control())