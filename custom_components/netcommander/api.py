
import asyncio
import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class NetCommanderAPI:
    """A stateful API for the Synaccess netCommander device using a persistent session."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize the API."""
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}"
        self._session: aiohttp.ClientSession | None = None

    async def async_login(self) -> bool:
        """Create a session and log in to the device, storing the session cookie."""
        self._session = aiohttp.ClientSession()
        login_url = f"{self.base_url}/login.cgi"
        login_data = {"Username": self.username, "Password": self.password}

        _LOGGER.debug(f"Attempting login to {login_url}")
        try:
            async with self._session.post(login_url, data=login_data, timeout=10) as resp:
                _LOGGER.debug(f"Login response status: {resp.status}")
                # The web UI redirects to /index.htm on successful login.
                if resp.status == 200 and "index.htm" in str(resp.url):
                    _LOGGER.info("Login successful, session cookie stored.")
                    return True
                _LOGGER.error("Login failed. Status: %s, URL: %s", resp.status, resp.url)
                await self.async_close()  # Clean up the failed session
                return False
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error(f"Error during login: {err}")
            await self.async_close() # Ensure session is cleaned up on error
            return False

    async def async_get_status(self) -> str | None:
        """Get the status of all outlets using the active session."""
        if not self._session:
            _LOGGER.error("Cannot get status, not logged in.")
            return None

        url = f"{self.base_url}/cmd.cgi?$A5"
        _LOGGER.debug(f"Getting status from {url}")
        try:
            async with self._session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.text()
                _LOGGER.error(f"Error getting status: {resp.status}")
                return None
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error(f"Error getting status: {err}")
            return None

    async def async_set_outlet(self, outlet: int, state: bool) -> bool:
        """Set the state of an outlet using the active session."""
        if not self._session:
            _LOGGER.error("Cannot set outlet, not logged in.")
            return False

        url = f"{self.base_url}/cmd.cgi?$A3,{outlet},{int(state)}"
        _LOGGER.debug(f"Setting outlet state for {outlet} via {url}")
        try:
            async with self._session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return "$A0" in text
                return False
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error(f"Error setting outlet state: {err}")
            return False

    async def async_close(self) -> None:
        """Close the client session."""
        if self._session:
            await self._session.close()
            _LOGGER.info("API session closed.")
            self._session = None
