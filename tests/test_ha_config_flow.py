"""Tests for Home Assistant config flow."""
import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from custom_components.netcommander.config_flow import ConfigFlow, CannotConnect, InvalidAuth
from custom_components.netcommander.const import DOMAIN
from netcommander import DeviceInfo
from netcommander.exceptions import AuthenticationError, ConnectionError as NetCommanderConnectionError


@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    from unittest.mock import MagicMock
    hass = MagicMock()
    hass.data = {}
    return hass


class TestConfigFlow:
    """Test the config flow."""

    @pytest.mark.asyncio
    async def test_form(self, mock_hass):
        """Test we get the form."""
        flow = ConfigFlow()
        flow.hass = mock_hass

        result = await flow.async_step_user()

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"] == {}

    @pytest.mark.asyncio
    async def test_user_success(self, mock_hass, device_info):
        """Test successful user step."""
        flow = ConfigFlow()
        flow.hass = mock_hass

        # Mock validate_input
        with patch(
            "custom_components.netcommander.config_flow.validate_input",
            return_value={
                "title": "NetCommander NP0501DU",
                "unique_id": "0C:73:EB:B0:9E:5C",
                "model": "NP0501DU",
            },
        ):
            result = await flow.async_step_user(
                {
                    CONF_HOST: "192.168.1.100",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "admin",
                }
            )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["title"] == "NetCommander NP0501DU"
        assert result["data"] == {
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "admin",
        }

    @pytest.mark.asyncio
    async def test_user_cannot_connect(self, mock_hass):
        """Test connection error."""
        flow = ConfigFlow()
        flow.hass = mock_hass

        with patch(
            "custom_components.netcommander.config_flow.validate_input",
            side_effect=CannotConnect,
        ):
            result = await flow.async_step_user(
                {
                    CONF_HOST: "192.168.1.100",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "admin",
                }
            )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}

    @pytest.mark.asyncio
    async def test_user_invalid_auth(self, mock_hass):
        """Test invalid authentication."""
        flow = ConfigFlow()
        flow.hass = mock_hass

        with patch(
            "custom_components.netcommander.config_flow.validate_input",
            side_effect=InvalidAuth,
        ):
            result = await flow.async_step_user(
                {
                    CONF_HOST: "192.168.1.100",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "wrong",
                }
            )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"] == {"base": "invalid_auth"}

    @pytest.mark.asyncio
    async def test_user_unknown_error(self, mock_hass):
        """Test unknown error."""
        flow = ConfigFlow()
        flow.hass = mock_hass

        with patch(
            "custom_components.netcommander.config_flow.validate_input",
            side_effect=Exception("Unknown error"),
        ):
            result = await flow.async_step_user(
                {
                    CONF_HOST: "192.168.1.100",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "admin",
                }
            )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"] == {"base": "unknown"}


class TestValidateInput:
    """Test the validate_input function."""

    @pytest.mark.asyncio
    async def test_validate_input_success(self, mock_hass, device_info):
        """Test successful validation."""
        from custom_components.netcommander.config_flow import validate_input

        with patch("netcommander.NetCommanderClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_device_info = AsyncMock(return_value=device_info)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            result = await validate_input(
                mock_hass,
                {
                    CONF_HOST: "192.168.1.100",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "admin",
                },
            )

        assert result["title"] == "NetCommander NP0501DU"
        assert result["unique_id"] == "0C:73:EB:B0:9E:5C"
        assert result["model"] == "NP0501DU"

    @pytest.mark.asyncio
    async def test_validate_input_no_mac(self, mock_hass):
        """Test validation when MAC address is not available."""
        from custom_components.netcommander.config_flow import validate_input

        device_info = DeviceInfo(
            model="NP0501DU",
            hardware_version="4.3",
            firmware_version="-7.72-8.5",
            bootloader_version="1.6",
            mac_address=None,
            raw_response="$A0,NP0501DU, HW4.3 BL1.6 -7.72-8.5",
        )

        with patch("netcommander.NetCommanderClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_device_info = AsyncMock(return_value=device_info)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            result = await validate_input(
                mock_hass,
                {
                    CONF_HOST: "192.168.1.100",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "admin",
                },
            )

        # Should fall back to IP address as unique_id
        assert result["unique_id"] == "192.168.1.100"

    @pytest.mark.asyncio
    async def test_validate_input_auth_error(self, mock_hass):
        """Test validation with authentication error."""
        from custom_components.netcommander.config_flow import validate_input

        with patch("netcommander.NetCommanderClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_device_info = AsyncMock(
                side_effect=AuthenticationError("Invalid credentials")
            )
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            with pytest.raises(InvalidAuth):
                await validate_input(
                    mock_hass,
                    {
                        CONF_HOST: "192.168.1.100",
                        CONF_USERNAME: "admin",
                        CONF_PASSWORD: "wrong",
                    },
                )

    @pytest.mark.asyncio
    async def test_validate_input_connection_error(self, mock_hass):
        """Test validation with connection error."""
        from custom_components.netcommander.config_flow import validate_input

        with patch("netcommander.NetCommanderClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_device_info = AsyncMock(
                side_effect=NetCommanderConnectionError("192.168.1.100", "Connection failed")
            )
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            with pytest.raises(CannotConnect):
                await validate_input(
                    mock_hass,
                    {
                        CONF_HOST: "192.168.1.100",
                        CONF_USERNAME: "admin",
                        CONF_PASSWORD: "admin",
                    },
                )
