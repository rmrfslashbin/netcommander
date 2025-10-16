"""Data update coordinator for NetCommander."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .lib.netcommander_lib import NetCommanderClient, DeviceStatus, DeviceInfo
from .lib.netcommander_lib.exceptions import NetCommanderError

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NetCommanderCoordinator(DataUpdateCoordinator[DeviceStatus]):
    """Coordinator to manage fetching NetCommander data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self.username = username
        self.password = password
        self.client = NetCommanderClient(host, username, password)
        self.device_info: DeviceInfo | None = None

    async def _async_update_data(self) -> DeviceStatus:
        """Fetch data from the device."""
        try:
            # Get device info on first update
            if self.device_info is None:
                self.device_info = await self.client.get_device_info()
                _LOGGER.debug(
                    "Device info retrieved: %s %s",
                    self.device_info.model,
                    self.device_info.firmware_version,
                )

            # Get current status
            status = await self.client.get_status()
            _LOGGER.debug(
                "Status updated: %d outlets on, %.2fA current",
                len(status.outlets_on),
                status.total_current_amps,
            )
            return status

        except NetCommanderError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await self.client.close()

    async def async_turn_on(self, outlet_number: int) -> bool:
        """Turn on an outlet."""
        try:
            result = await self.client.turn_on(outlet_number)
            await self.async_request_refresh()
            return result
        except NetCommanderError as err:
            _LOGGER.error("Failed to turn on outlet %d: %s", outlet_number, err)
            return False

    async def async_turn_off(self, outlet_number: int) -> bool:
        """Turn off an outlet."""
        try:
            result = await self.client.turn_off(outlet_number)
            await self.async_request_refresh()
            return result
        except NetCommanderError as err:
            _LOGGER.error("Failed to turn off outlet %d: %s", outlet_number, err)
            return False

    async def async_reboot_outlet(self, outlet_number: int) -> bool:
        """Reboot an outlet (off, wait, on)."""
        try:
            # Turn off
            await self.client.turn_off(outlet_number)
            # Wait 5 seconds
            await asyncio.sleep(5)
            # Turn on
            result = await self.client.turn_on(outlet_number)
            await self.async_request_refresh()
            return result
        except NetCommanderError as err:
            _LOGGER.error("Failed to reboot outlet %d: %s", outlet_number, err)
            return False
