"""API for Synaccess netCommander."""

import asyncio

import aiohttp


class NetCommanderAPI:
    """The API for the Synaccess netCommander device."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Initialize the API."""
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}/cmd.cgi"

    async def async_login(self) -> bool:
        """Log in to the device."""
        url = f"{self.base_url}?$A1,{self.username},{self.password}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()
                return "$A0" in text

    async def async_get_status(self) -> str | None:
        """Get the status of all outlets."""
        url = f"{self.base_url}?$A5"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.text()
                return None

    async def async_set_outlet(self, outlet: int, state: bool) -> bool:
        """Set the state of an outlet."""
        url = f"{self.base_url}?$A3,{outlet},{int(state)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()
                return "$A0" in text
