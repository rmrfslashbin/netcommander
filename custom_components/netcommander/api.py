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
        params = {"cmd": "$A1", "Arg1": self.username, "Arg2": self.password}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as resp:
                text = await resp.text()
                return "$A0" in text

    async def async_get_status(self) -> str | None:
        """Get the status of all outlets."""
        params = {"cmd": "$A5"}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as resp:
                if resp.status == 200:
                    return await resp.text()
                return None

    async def async_set_outlet(self, outlet: int, state: bool) -> bool:
        """Set the state of an outlet."""
        params = {"cmd": "$A3", "Arg1": outlet, "Arg2": int(state)}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as resp:
                text = await resp.text()
                return "$A0" in text
