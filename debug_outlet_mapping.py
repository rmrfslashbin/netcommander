#!/usr/bin/env python3
"""Debug script to test outlet mapping."""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

class DebugAPI:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.base_url = f"http://{host}"
        self._auth = aiohttp.BasicAuth(username, password)
        self._session = None

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(auth=self._auth)

    async def close(self):
        if self._session:
            await self._session.close()

    async def get_status(self):
        await self._ensure_session()
        async with self._session.get(f"{self.base_url}/cmd.cgi?$A5") as resp:
            if resp.status == 200:
                return await resp.text()
        return None

    async def toggle_outlet(self, rly_index):
        await self._ensure_session()
        url = f"{self.base_url}/cmd.cgi?rly={rly_index}"
        print(f"Sending: {url}")
        async with self._session.get(url) as resp:
            if resp.status == 200:
                result = await resp.text()
                print(f"Response: {result}")
                return result
        return None

async def main():
    api = DebugAPI(
        os.getenv("HOST", "192.168.50.227"),
        os.getenv("USER", "admins"),
        os.getenv("PASSWORD", "admin123")
    )

    try:
        print("=== Initial Status ===")
        status = await api.get_status()
        print(f"Status: {status}")
        
        if status:
            parts = status.strip().split(",")
            if len(parts) >= 2:
                outlets = parts[1]
                print(f"Outlet states: {outlets}")
                for i, state in enumerate(outlets):
                    print(f"  Outlet position {i}: {state} ({'ON' if state == '1' else 'OFF'})")

        print("\n=== Testing rly=0 (should be outlet 1) ===")
        await api.toggle_outlet(0)
        await asyncio.sleep(1)
        
        status = await api.get_status()
        print(f"After rly=0: {status}")
        if status:
            parts = status.strip().split(",")
            if len(parts) >= 2:
                outlets = parts[1]
                print(f"New outlet states: {outlets}")
                for i, state in enumerate(outlets):
                    print(f"  Outlet position {i}: {state} ({'ON' if state == '1' else 'OFF'})")

        print("\n=== Testing rly=1 (should be outlet 2) ===")
        await api.toggle_outlet(1)
        await asyncio.sleep(1)
        
        status = await api.get_status()
        print(f"After rly=1: {status}")
        if status:
            parts = status.strip().split(",")
            if len(parts) >= 2:
                outlets = parts[1]
                print(f"New outlet states: {outlets}")
                for i, state in enumerate(outlets):
                    print(f"  Outlet position {i}: {state} ({'ON' if state == '1' else 'OFF'})")

        print("\n=== Testing each rly index ===")
        for rly_idx in range(5):
            print(f"\n--- Testing rly={rly_idx} ---")
            before = await api.get_status()
            before_outlets = before.strip().split(",")[1] if before else "unknown"
            print(f"Before: {before_outlets}")
            
            await api.toggle_outlet(rly_idx)
            await asyncio.sleep(1)
            
            after = await api.get_status()
            after_outlets = after.strip().split(",")[1] if after else "unknown"
            print(f"After:  {after_outlets}")
            
            # Find which outlet changed
            if before_outlets != "unknown" and after_outlets != "unknown":
                for i, (b, a) in enumerate(zip(before_outlets, after_outlets)):
                    if b != a:
                        print(f"  -> rly={rly_idx} controls outlet position {i}")
                        break
            
            # Toggle back
            await api.toggle_outlet(rly_idx)
            await asyncio.sleep(1)

    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(main())