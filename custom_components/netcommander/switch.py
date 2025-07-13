"""Switch platform for Synaccess netCommander."""

from __future__ import annotations
import asyncio
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
from .coordinator import NetCommanderDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the netCommander switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NetCommanderSwitch(coordinator, outlet)
        for outlet in coordinator.data["outlets"])


class NetCommanderSwitch(CoordinatorEntity[NetCommanderDataUpdateCoordinator], SwitchEntity):
    """Representation of a netCommander switch."""

    def __init__(self, coordinator: NetCommanderDataUpdateCoordinator, outlet: int) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.outlet = outlet
        # Map HA outlet numbers to physical outlet numbers
        # HA 1→HW 5, HA 2→HW 4, HA 3→HW 3, HA 4→HW 2, HA 5→HW 1
        physical_outlet_map = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
        physical_outlet = physical_outlet_map[outlet]
        self._attr_name = f"Physical Outlet {physical_outlet}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{outlet}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"netCommander {coordinator.api.host}",
            manufacturer="Synaccess Networks",
            model="NP-0501DU",  # From our testing - 5-outlet model
            sw_version="2.0.12",
            configuration_url=f"http://{coordinator.api.host}",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        state = self.coordinator.data["outlets"].get(self.outlet, False)
        _LOGGER.debug(f"Outlet {self.outlet} state check: {state} (data: {self.coordinator.data['outlets']})")
        return state

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        _LOGGER.debug(f"Turning outlet {self.outlet} ON")
        success = await self.coordinator.api.async_set_outlet(self.outlet, True)
        _LOGGER.debug(f"Outlet {self.outlet} turn ON result: {success}")
        if success:
            # Optimistically update the state immediately
            self.coordinator.data["outlets"][self.outlet] = True
            self.async_write_ha_state()
            
            # Give device time to process command before refreshing
            await asyncio.sleep(1.0)  # Wait 1 second
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        _LOGGER.debug(f"Turning outlet {self.outlet} OFF")
        success = await self.coordinator.api.async_set_outlet(self.outlet, False)
        _LOGGER.debug(f"Outlet {self.outlet} turn OFF result: {success}")
        if success:
            # Optimistically update the state immediately
            self.coordinator.data["outlets"][self.outlet] = False
            self.async_write_ha_state()
            
            # Give device time to process command before refreshing
            await asyncio.sleep(1.0)  # Wait 1 second
            await self.coordinator.async_request_refresh()
