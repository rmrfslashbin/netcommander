"""Sensor platform for Synaccess netCommander."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NetCommanderDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the netCommander sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for outlet_id in coordinator.data["outlets"]:
        sensors.append(NetCommanderCurrentSensor(coordinator, outlet_id))

    sensors.append(NetCommanderTemperatureSensor(coordinator))
    async_add_entities(sensors)


class NetCommanderCurrentSensor(CoordinatorEntity[NetCommanderDataUpdateCoordinator], SensorEntity):
    """Representation of a netCommander current sensor."""

    entity_description = SensorEntityDescription(
        key="current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    )

    def __init__(self, coordinator: NetCommanderDataUpdateCoordinator, outlet_id: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.outlet_id = outlet_id
        self._attr_name = f"Outlet {outlet_id} Current"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{outlet_id}_current"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data["sensors"]["current"][self.outlet_id]


class NetCommanderTemperatureSensor(CoordinatorEntity[NetCommanderDataUpdateCoordinator], SensorEntity):
    """Representation of a netCommander temperature sensor."""

    entity_description = SensorEntityDescription(
        key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    )

    def __init__(self, coordinator: NetCommanderDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Device Temperature"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_temperature"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data["sensors"]["temperature"]
