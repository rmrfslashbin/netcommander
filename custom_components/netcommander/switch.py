"""Switch platform for Synaccess NetCommander outlets."""
from __future__ import annotations

from typing import Any
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, ATTR_OUTLET_NUMBER
from .coordinator import NetCommanderCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NetCommander switches."""
    coordinator: NetCommanderCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create switch for each outlet (1-5)
    entities = [
        NetCommanderSwitch(coordinator, entry, outlet_num)
        for outlet_num in range(1, 6)
    ]

    async_add_entities(entities)


class NetCommanderSwitch(CoordinatorEntity[NetCommanderCoordinator], SwitchEntity):
    """Representation of a NetCommander outlet switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NetCommanderCoordinator,
        entry: ConfigEntry,
        outlet_number: int,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.outlet_number = outlet_number
        self._attr_unique_id = f"{entry.entry_id}_outlet_{outlet_number}"
        self._attr_name = f"Outlet {outlet_number}"

        # Device info
        device_info = coordinator.device_info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{MANUFACTURER} {device_info.model if device_info else 'NetCommander'}",
            "manufacturer": MANUFACTURER,
            "model": device_info.model if device_info else "Unknown",
            "sw_version": device_info.firmware_version if device_info else None,
            "hw_version": device_info.hardware_version if device_info else None,
            "configuration_url": f"http://{coordinator.host}",
        }

    @property
    def is_on(self) -> bool:
        """Return true if outlet is on."""
        if self.coordinator.data:
            return self.coordinator.data.outlets.get(self.outlet_number, False)
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            ATTR_OUTLET_NUMBER: self.outlet_number,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the outlet on."""
        await self.coordinator.async_turn_on(self.outlet_number)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the outlet off."""
        await self.coordinator.async_turn_off(self.outlet_number)
