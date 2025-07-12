"""Switch platform for Synaccess netCommander."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
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
        self._attr_name = f"Outlet {outlet}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{outlet}"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data["outlets"][self.outlet]

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.api.async_set_outlet(self.outlet, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.api.async_set_outlet(self.outlet, False)
        await self.coordinator.async_request_refresh()
