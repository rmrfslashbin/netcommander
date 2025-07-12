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
            
            # Expected format: $A0,11111,0.07,XX
            # parts[0] = "$A0" (success indicator)
            # parts[1] = "11111" (outlet states)
            # parts[2] = "0.07" (total current)
            # parts[3] = "XX" (temperature or other data)
            
            if len(parts) < 4 or not parts[0].startswith("$A0"):
                raise UpdateFailed(f"Invalid status response: {status_str}")
                
            outlets = parts[1]
            total_current = float(parts[2])
            temp_str = parts[3]
            
            # Parse temperature - handle "XX" or numeric values
            try:
                temperature = int(temp_str) if temp_str.isdigit() else 0
            except (ValueError, AttributeError):
                temperature = 0

            return {
                "outlets": {i + 1: outlets[i] == "1" for i in range(len(outlets))},
                "sensors": {
                    "total_current": total_current,
                    "temperature": temperature,
                },
            }
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception
