"""Button platform for Synaccess netCommander."""

from __future__ import annotations
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import NetCommanderDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the netCommander buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NetCommanderRebootButton(coordinator, outlet)
        for outlet in coordinator.data["outlets"])


class NetCommanderRebootButton(CoordinatorEntity[NetCommanderDataUpdateCoordinator], ButtonEntity):
    """Representation of a netCommander reboot button."""

    def __init__(self, coordinator: NetCommanderDataUpdateCoordinator, outlet: int) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.outlet = outlet
        # Map HA outlet numbers to physical outlet numbers
        # HA 1→HW 5, HA 2→HW 4, HA 3→HW 3, HA 4→HW 2, HA 5→HW 1
        physical_outlet_map = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
        physical_outlet = physical_outlet_map[outlet]
        self._attr_name = f"Reboot Physical Outlet {physical_outlet}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{outlet}_reboot"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"netCommander {coordinator.api.host}",
            manufacturer="Synaccess Networks",
            model="NP-0501DU",  # Tested model - may work with other netBooter/netCommander models
            sw_version="2.1.1",
            configuration_url=f"http://{coordinator.api.host}",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug(f"Rebooting outlet {self.outlet}")
        success = await self.coordinator.api.async_reboot_outlet(self.outlet)
        _LOGGER.debug(f"Outlet {self.outlet} reboot result: {success}")
        if success:
            # Refresh status after a delay to catch state changes
            await self.coordinator.async_request_refresh()