"""DataUpdateCoordinator for Synaccess netCommander."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NetCommanderAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class NetCommanderDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = NetCommanderAPI(
            entry.data[CONF_HOST],
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await self.api.close()

    async def _async_update_data(self):
        """Update data via library."""
        try:
            status_str = await self.api.async_get_status()
            if status_str is None:
                raise UpdateFailed("No status returned")

            parts = status_str.strip().split(",")
            outlets = parts[0]
            currents = parts[1:5]
            temp = parts[5]

            return {
                "outlets": {i + 1: outlets[i] == "1" for i in range(len(outlets))},
                "sensors": {
                    "current": {i + 1: float(currents[i]) / 10.0 for i in range(len(currents))},
                    "temperature": int(temp),
                },
            }
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception
