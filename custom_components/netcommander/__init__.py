"""The Synaccess netCommander integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL,
    CONF_REBOOT_DELAY,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_REBOOT_DELAY,
    ATTR_OUTLET_NUMBER,
)
from .coordinator import NetCommanderCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.SENSOR, Platform.BUTTON]

# Service schemas
SERVICE_TURN_ON_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_OUTLET_NUMBER): cv.positive_int,
    }
)

SERVICE_TURN_OFF_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_OUTLET_NUMBER): cv.positive_int,
    }
)

SERVICE_REBOOT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_OUTLET_NUMBER): cv.positive_int,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Synaccess netCommander from a config entry."""
    _LOGGER.debug("Setting up netCommander integration")

    # Get options from config entry, fallback to defaults
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    reboot_delay = entry.options.get(CONF_REBOOT_DELAY, DEFAULT_REBOOT_DELAY)

    coordinator = NetCommanderCoordinator(
        hass,
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        scan_interval=scan_interval,
        reboot_delay=reboot_delay,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_turn_on(call: ServiceCall) -> None:
        """Handle turn on service call."""
        outlet_number = call.data[ATTR_OUTLET_NUMBER]
        device_id = call.data.get("device_id")

        if device_id:
            coordinator = await _get_coordinator_for_device(hass, device_id)
            if coordinator:
                await coordinator.async_turn_on(outlet_number)

    async def handle_turn_off(call: ServiceCall) -> None:
        """Handle turn off service call."""
        outlet_number = call.data[ATTR_OUTLET_NUMBER]
        device_id = call.data.get("device_id")

        if device_id:
            coordinator = await _get_coordinator_for_device(hass, device_id)
            if coordinator:
                await coordinator.async_turn_off(outlet_number)

    async def handle_reboot(call: ServiceCall) -> None:
        """Handle reboot service call."""
        outlet_number = call.data[ATTR_OUTLET_NUMBER]
        device_id = call.data.get("device_id")

        if device_id:
            coordinator = await _get_coordinator_for_device(hass, device_id)
            if coordinator:
                await coordinator.async_reboot_outlet(outlet_number)

    async def handle_turn_on_all(call: ServiceCall) -> None:
        """Handle turn on all service call."""
        device_id = call.data.get("device_id")

        if device_id:
            coordinator = await _get_coordinator_for_device(hass, device_id)
            if coordinator and coordinator.data:
                for outlet_num in coordinator.data.outlets.keys():
                    await coordinator.async_turn_on(outlet_num)

    async def handle_turn_off_all(call: ServiceCall) -> None:
        """Handle turn off all service call."""
        device_id = call.data.get("device_id")

        if device_id:
            coordinator = await _get_coordinator_for_device(hass, device_id)
            if coordinator and coordinator.data:
                for outlet_num in coordinator.data.outlets.keys():
                    await coordinator.async_turn_off(outlet_num)

    # Register services if not already registered
    if not hass.services.has_service(DOMAIN, "turn_on"):
        hass.services.async_register(
            DOMAIN, "turn_on", handle_turn_on, schema=SERVICE_TURN_ON_SCHEMA
        )
    if not hass.services.has_service(DOMAIN, "turn_off"):
        hass.services.async_register(
            DOMAIN, "turn_off", handle_turn_off, schema=SERVICE_TURN_OFF_SCHEMA
        )
    if not hass.services.has_service(DOMAIN, "reboot"):
        hass.services.async_register(
            DOMAIN, "reboot", handle_reboot, schema=SERVICE_REBOOT_SCHEMA
        )
    if not hass.services.has_service(DOMAIN, "turn_on_all"):
        hass.services.async_register(DOMAIN, "turn_on_all", handle_turn_on_all)
    if not hass.services.has_service(DOMAIN, "turn_off_all"):
        hass.services.async_register(DOMAIN, "turn_off_all", handle_turn_off_all)

    return True


async def _get_coordinator_for_device(
    hass: HomeAssistant, device_id: str
) -> NetCommanderCoordinator | None:
    """Get coordinator for a specific device ID."""
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get(device_id)

    if not device_entry:
        _LOGGER.error("Device %s not found", device_id)
        return None

    # Find the config entry for this device
    for entry_id in device_entry.config_entries:
        if entry_id in hass.data.get(DOMAIN, {}):
            return hass.data[DOMAIN][entry_id]

    _LOGGER.error("No coordinator found for device %s", device_id)
    return None


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading netCommander integration")

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: NetCommanderCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

        # Unregister services if this is the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "turn_on")
            hass.services.async_remove(DOMAIN, "turn_off")
            hass.services.async_remove(DOMAIN, "reboot")
            hass.services.async_remove(DOMAIN, "turn_on_all")
            hass.services.async_remove(DOMAIN, "turn_off_all")

    return unload_ok
