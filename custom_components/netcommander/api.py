"""API for Synaccess netCommander."""

import logging
from typing import Optional
import aiohttp

_LOGGER = logging.getLogger(__name__)


class NetCommanderAPI:
    """The API for the Synaccess netCommander device."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize the API."""
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._auth = aiohttp.BasicAuth(username, password)

    async def _ensure_session(self) -> None:
        """Ensure we have an active session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                auth=self._auth,
                headers={'User-Agent': 'NetCommander-HA/2.0'}
            )

    async def close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def async_login(self) -> bool:
        """Test connection to the device."""
        await self._ensure_session()
        try:
            async with self._session.get(f"{self.base_url}/cmd.cgi?$A5") as resp:
                return resp.status == 200
        except Exception as e:
            _LOGGER.error(f"Connection test failed: {e}")
            return False

    async def async_get_status(self) -> str | None:
        """Get the status of all outlets."""
        await self._ensure_session()
        try:
            async with self._session.get(f"{self.base_url}/cmd.cgi?$A5") as resp:
                if resp.status == 200:
                    return await resp.text()
                return None
        except Exception as e:
            _LOGGER.error(f"Failed to get status: {e}")
            return None

    async def async_set_outlet(self, outlet: int, state: bool) -> bool:
        """Set the state of an outlet."""
        await self._ensure_session()
        
        # Convert to rly command index (device uses reverse numbering)
        # HA outlet 1 = rly=4, HA outlet 2 = rly=3, ..., HA outlet 5 = rly=0
        rly_index = 5 - outlet
        
        # For status checking, HA outlet matches string position directly
        status_position = outlet - 1
        
        # Get current state first to determine if we need to toggle
        current_status = await self.async_get_status()
        if current_status is None:
            return False
            
        # Parse current state
        parts = current_status.strip().split(",")
        _LOGGER.debug(f"Status response: {current_status}")
        if len(parts) < 2:
            return False
            
        current_outlets = parts[1]
        _LOGGER.debug(f"Current outlets string: '{current_outlets}'")
        _LOGGER.debug(f"Outlet {outlet} (rly={rly_index}) status position {status_position}: '{current_outlets[status_position] if status_position < len(current_outlets) else 'INVALID'}')")
        if status_position >= len(current_outlets):
            return False
            
        current_state = current_outlets[status_position] == "1"
        
        # Only send command if state needs to change
        if current_state == state:
            _LOGGER.debug(f"Outlet {outlet} already in desired state ({state})")
            return True
            
        # Use simple toggle command with correct rly mapping
        url = f"{self.base_url}/cmd.cgi?rly={rly_index}"
        _LOGGER.debug(f"Toggling outlet {outlet} (rly={rly_index}) from {current_state} to {state}")
        
        try:
            async with self._session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return "$A0" in text
                return False
        except Exception as e:
            _LOGGER.error(f"Failed to set outlet {outlet}: {e}")
            return False
    
    async def async_reboot_outlet(self, outlet: int) -> bool:
        """Reboot an outlet (power cycle)."""
        await self._ensure_session()
        
        # Convert to rb command index (device uses reverse numbering)
        # HA outlet 1 = rb=4, HA outlet 2 = rb=3, ..., HA outlet 5 = rb=0
        rb_index = 5 - outlet
        
        url = f"{self.base_url}/cmd.cgi?rb={rb_index}"
        _LOGGER.debug(f"Rebooting outlet {outlet} (rb={rb_index})")
        
        try:
            async with self._session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return "$A0" in text
                return False
        except Exception as e:
            _LOGGER.error(f"Failed to reboot outlet {outlet}: {e}")
            return False
