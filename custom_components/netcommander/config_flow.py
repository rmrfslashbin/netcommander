"""Config flow for Synaccess NetCommander integration."""
from __future__ import annotations

import logging
from typing import Any
import sys
import os

# Add bundled lib to path for netcommander library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from netcommander import NetCommanderClient
from netcommander.exceptions import AuthenticationError, ConnectionError as NetCommanderConnectionError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME, default="admin"): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    client = NetCommanderClient(
        data[CONF_HOST],
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
    )

    try:
        # Test connection by getting device info
        device_info = await client.get_device_info()

        # Return info for unique_id and title
        return {
            "title": f"NetCommander {device_info.model}",
            "unique_id": device_info.mac_address or data[CONF_HOST],
            "model": device_info.model,
        }
    except AuthenticationError as err:
        raise InvalidAuth from err
    except NetCommanderConnectionError as err:
        raise CannotConnect from err
    finally:
        await client.close()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Synaccess NetCommander."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID based on MAC address or IP
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
