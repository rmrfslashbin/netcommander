"""
NetCommander API Client with proper HTTP Basic Authentication

This implementation uses standard HTTP Basic Auth, which the device
actually supports (contrary to the previous implementation's assumptions).
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OutletStatus:
    """Status of a single outlet"""
    outlet_id: int
    is_on: bool
    current: float  # In amperes


@dataclass
class DeviceStatus:
    """Complete device status"""
    outlets: List[OutletStatus]
    temperature: int  # In Celsius
    total_current: float  # Total current draw
    raw_response: str  # For debugging


class NetCommanderAPI:
    """API client for Synaccess netCommander devices"""
    
    def __init__(self, host: str, username: str, password: str):
        """Initialize the API client
        
        Args:
            host: IP address or hostname of the device
            username: Device username
            password: Device password
        """
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._auth = aiohttp.BasicAuth(username, password)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def connect(self):
        """Create the HTTP session"""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                auth=self._auth,
                headers={'User-Agent': 'NetCommander-HA/2.0'}
            )
            
    async def close(self):
        """Close the HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None
            
    async def test_connection(self) -> bool:
        """Test if we can connect and authenticate
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self.connect()
            async with self._session.get(f"{self.base_url}/cmd.cgi") as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
            
    async def get_status(self) -> DeviceStatus:
        """Get complete device status
        
        Returns:
            DeviceStatus object with all outlet states and sensor readings
            
        Raises:
            aiohttp.ClientError: On connection/auth failure
            ValueError: On invalid response format
        """
        await self.connect()
        
        # Send status command ($A5)
        async with self._session.get(f"{self.base_url}/cmd.cgi?$A5") as resp:
            if resp.status == 401:
                raise aiohttp.ClientError("Authentication failed")
            elif resp.status != 200:
                raise aiohttp.ClientError(f"Request failed with status {resp.status}")
                
            text = await resp.text()
            return self._parse_status(text)
            
    def _parse_status(self, response: str) -> DeviceStatus:
        """Parse the status response
        
        Expected format: $A0,11111,0.06,XX
        - $A0: Success code
        - 11111: Outlet states (1=on, 0=off)
        - 0.06: Current in 0.1A units
        - XX: Temperature or additional data
        
        Args:
            response: Raw response from device
            
        Returns:
            Parsed DeviceStatus
            
        Raises:
            ValueError: If response format is invalid
        """
        response = response.strip()
        parts = response.split(',')
        
        if len(parts) < 3 or not parts[0].startswith('$A0'):
            raise ValueError(f"Invalid status response: {response}")
            
        # Parse outlet states
        outlet_states = parts[1]
        outlets = []
        for i, state in enumerate(outlet_states):
            outlets.append(OutletStatus(
                outlet_id=i + 1,
                is_on=(state == '1'),
                current=0.0  # Individual currents not provided in basic status
            ))
            
        # Parse total current (convert from 0.01A to A)
        try:
            total_current = float(parts[2])
        except (ValueError, IndexError):
            total_current = 0.0
            
        # Parse temperature if available
        temperature = 0
        if len(parts) > 3:
            temp_str = parts[3]
            # Try to parse temperature, handle 'XX' or other non-numeric values
            try:
                temperature = int(temp_str)
            except ValueError:
                logger.debug(f"Could not parse temperature: {temp_str}")
                
        return DeviceStatus(
            outlets=outlets,
            temperature=temperature,
            total_current=total_current,
            raw_response=response
        )
        
    async def set_outlet(self, outlet_id: int, state: bool) -> bool:
        """Turn an outlet on or off
        
        Args:
            outlet_id: Outlet number (1-based, converted to 0-based internally)
            state: True for on, False for off
            
        Returns:
            True if successful, False otherwise
        """
        await self.connect()
        
        # Convert to 0-based index (device uses 0-4, API uses 1-5)
        zero_based_id = outlet_id - 1
        
        # Use rly command with explicit state
        state_value = 1 if state else 0
        url = f"{self.base_url}/cmd.cgi?rly={zero_based_id}&state={state_value}"
        
        async with self._session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Failed to set outlet {outlet_id}: HTTP {resp.status}")
                return False
                
            text = await resp.text()
            logger.debug(f"Set outlet response: {text}")
            
            # Check response
            if "$A0" in text:
                return True
            elif "$AF" in text:
                logger.warning(f"Outlet control failed - device returned error.")
                return False
            else:
                logger.error(f"Unexpected response: {text}")
                return False
            
    async def set_all_outlets(self, state: bool) -> bool:
        """Turn all outlets on or off
        
        Args:
            state: True for on, False for off
            
        Returns:
            True if successful, False otherwise
        """
        await self.connect()
        
        # Send all outlets command ($A7)
        state_value = 1 if state else 0
        url = f"{self.base_url}/cmd.cgi?$A7,{state_value}"
        
        async with self._session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Failed to set all outlets: HTTP {resp.status}")
                return False
                
            text = await resp.text()
            return "$A0" in text
            
    async def toggle_outlet(self, outlet_id: int) -> bool:
        """Toggle an outlet (flip its current state)
        
        Args:
            outlet_id: Outlet number (1-based)
            
        Returns:
            True if successful, False otherwise
        """
        await self.connect()
        
        # Convert to 0-based index
        zero_based_id = outlet_id - 1
        
        # Use simple rly command for toggle
        url = f"{self.base_url}/cmd.cgi?rly={zero_based_id}"
        
        async with self._session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Failed to toggle outlet {outlet_id}: HTTP {resp.status}")
                return False
                
            text = await resp.text()
            logger.debug(f"Toggle outlet response: {text}")
            
            return "$A0" in text
            
    async def check_control_capability(self) -> Dict[str, bool]:
        """Check what control capabilities are available
        
        Returns:
            Dict with capability flags
        """
        capabilities = {
            'read_status': False,
            'control_outlets': False,
            'control_all': False,
            'reboot_outlets': False
        }
        
        await self.connect()
        
        # Test read capability
        try:
            status = await self.get_status()
            capabilities['read_status'] = True
            
            # Test outlet control (try to set outlet 1 to its current state)
            if status.outlets:
                current_state = status.outlets[0].is_on
                if await self.set_outlet(1, current_state):
                    capabilities['control_outlets'] = True
                    
                # Test all outlets control
                if await self.set_all_outlets(current_state):
                    capabilities['control_all'] = True
                    
        except Exception as e:
            logger.error(f"Capability check failed: {e}")
            
        return capabilities
    
    async def reboot_outlet(self, outlet_id: int, delay: int = 10) -> bool:
        """Reboot an outlet (turn off, wait, turn on)
        
        Args:
            outlet_id: Outlet number (1-based)
            delay: Seconds to wait between off and on
            
        Returns:
            True if successful, False otherwise
        """
        await self.connect()
        
        # Send reboot command ($A4)
        url = f"{self.base_url}/cmd.cgi?$A4,{outlet_id}"
        
        async with self._session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Failed to reboot outlet {outlet_id}: HTTP {resp.status}")
                return False
                
            text = await resp.text()
            return "$A0" in text


# Example usage for testing
async def main():
    """Test the API"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    async with NetCommanderAPI(host, username, password) as api:
        # Test connection
        if await api.test_connection():
            print("✅ Connection successful!")
            
            # Get status
            status = await api.get_status()
            print(f"\nDevice Status:")
            print(f"Temperature: {status.temperature}°C")
            print(f"Total Current: {status.total_current}A")
            print(f"Raw: {status.raw_response}")
            
            print("\nOutlets:")
            for outlet in status.outlets:
                state = "ON" if outlet.is_on else "OFF"
                print(f"  Outlet {outlet.outlet_id}: {state}")
                
            # Test toggling outlet 1
            print("\nToggling outlet 1...")
            current_state = status.outlets[0].is_on
            success = await api.set_outlet(1, not current_state)
            if success:
                print("✅ Toggle successful!")
            else:
                print("❌ Toggle failed!")
                
        else:
            print("❌ Connection failed!")


if __name__ == "__main__":
    asyncio.run(main())