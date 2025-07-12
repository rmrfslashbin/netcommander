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
        
        # Convert to 0-based index (device uses 0-4, HA uses 1-5)
        zero_based_outlet = outlet - 1
        
        # Get current state first to determine if we need to toggle
        current_status = await self.async_get_status()
        if current_status is None:
            return False
            
        # Parse current state
        parts = current_status.strip().split(",")
        if len(parts) < 2:
            return False
            
        current_outlets = parts[1]
        if zero_based_outlet >= len(current_outlets):
            return False
            
        current_state = current_outlets[zero_based_outlet] == "1"
        
        # Only send command if state needs to change
        if current_state == state:
            _LOGGER.debug(f"Outlet {outlet} already in desired state ({state})")
            return True
            
        # Use simple toggle command (this worked in our testing)
        url = f"{self.base_url}/cmd.cgi?rly={zero_based_outlet}"
        _LOGGER.debug(f"Toggling outlet {outlet} (rly={zero_based_outlet}) from {current_state} to {state}")
        
        try:
            async with self._session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return "$A0" in text
                return False
        except Exception as e:
            _LOGGER.error(f"Failed to set outlet {outlet}: {e}")
            return False
