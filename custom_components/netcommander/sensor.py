"""Sensor platform for Synaccess netCommander."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import NetCommanderDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the netCommander sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        NetCommanderTotalCurrentSensor(coordinator),
        NetCommanderTemperatureSensor(coordinator),
    ]
    async_add_entities(sensors)


class NetCommanderTotalCurrentSensor(CoordinatorEntity[NetCommanderDataUpdateCoordinator], SensorEntity):
    """Representation of a netCommander total current sensor."""

    entity_description = SensorEntityDescription(
        key="total_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    )

    def __init__(self, coordinator: NetCommanderDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Total Current"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_total_current"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"netCommander {coordinator.api.host}",
            manufacturer="Synaccess Networks",
            model="NP-0501DU",
            sw_version="2.0.10",
            configuration_url=f"http://{coordinator.api.host}",
        )

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data["sensors"]["total_current"]


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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"netCommander {coordinator.api.host}",
            manufacturer="Synaccess Networks",
            model="NP-0501DU", 
            sw_version="2.0.10",
            configuration_url=f"http://{coordinator.api.host}",
        )

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data["sensors"]["temperature"]
