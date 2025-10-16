"""Sensor platform for Synaccess NetCommander."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .lib.netcommander_lib import DeviceStatus

from .const import DOMAIN, MANUFACTURER
from .coordinator import NetCommanderCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class NetCommanderSensorDescription(SensorEntityDescription):
    """Describes NetCommander sensor entity."""

    value_fn: Callable[[DeviceStatus], Any] | None = None


SENSORS: tuple[NetCommanderSensorDescription, ...] = (
    NetCommanderSensorDescription(
        key="total_current",
        name="Total Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: status.total_current_amps,
    ),
    NetCommanderSensorDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: float(status.temperature) if status.temperature and status.temperature != "XX" else None,
    ),
    NetCommanderSensorDescription(
        key="outlets_on",
        name="Outlets On",
        icon="mdi:power-socket",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda status: len(status.outlets_on),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NetCommander sensors."""
    coordinator: NetCommanderCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        NetCommanderSensor(coordinator, entry, description)
        for description in SENSORS
    ]

    async_add_entities(entities)


class NetCommanderSensor(CoordinatorEntity[NetCommanderCoordinator], SensorEntity):
    """Representation of a NetCommander sensor."""

    entity_description: NetCommanderSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NetCommanderCoordinator,
        entry: ConfigEntry,
        description: NetCommanderSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

        # Device info
        device_info = coordinator.device_info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{MANUFACTURER} {device_info.model if device_info else 'NetCommander'}",
            "manufacturer": MANUFACTURER,
            "model": device_info.model if device_info else "Unknown",
            "sw_version": device_info.firmware_version if device_info else None,
            "hw_version": device_info.hardware_version if device_info else None,
            "connections": {("mac", device_info.mac_address)} if device_info and device_info.mac_address else set(),
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data and self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
