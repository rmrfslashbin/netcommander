"""Button platform for Synaccess NetCommander outlet reboot."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
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
    """Set up NetCommander buttons."""
    coordinator: NetCommanderCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create reboot button for each outlet (1-5)
    entities = [
        NetCommanderRebootButton(coordinator, entry, outlet_num)
        for outlet_num in range(1, 6)
    ]

    async_add_entities(entities)


class NetCommanderRebootButton(CoordinatorEntity[NetCommanderCoordinator], ButtonEntity):
    """Representation of a NetCommander outlet reboot button."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:restart"

    def __init__(
        self,
        coordinator: NetCommanderCoordinator,
        entry: ConfigEntry,
        outlet_number: int,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.outlet_number = outlet_number
        self._attr_unique_id = f"{entry.entry_id}_reboot_{outlet_number}"
        self._attr_name = f"Reboot Outlet {outlet_number}"

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
            "connections": {("mac", device_info.mac_address)} if device_info and device_info.mac_address else set(),
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Rebooting outlet %d", self.outlet_number)
        await self.coordinator.async_reboot_outlet(self.outlet_number)
