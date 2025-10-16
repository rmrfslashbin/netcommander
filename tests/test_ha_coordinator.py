"""Tests for Home Assistant coordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from homeassistant.helpers.update_coordinator import UpdateFailed

# Import after path setup
from custom_components.netcommander.coordinator import NetCommanderCoordinator
from netcommander import DeviceStatus, DeviceInfo
from netcommander.exceptions import NetCommanderError


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    return hass


class TestNetCommanderCoordinator:
    """Test NetCommanderCoordinator class."""

    @pytest.mark.asyncio
    async def test_coordinator_initialization(self, hass):
        """Test coordinator initialization."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )

        assert coordinator.host == "192.168.1.100"
        assert coordinator.username == "admin"
        assert coordinator.password == "admin"
        assert coordinator.update_interval == timedelta(seconds=30)
        assert coordinator.device_info is None

    @pytest.mark.asyncio
    async def test_coordinator_update_success(self, hass, device_status, device_info, mock_client):
        """Test successful data update."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )

        # Mock the client
        coordinator.client = mock_client

        # First update should fetch device info
        data = await coordinator._async_update_data()

        assert data == device_status
        assert coordinator.device_info == device_info
        mock_client.get_device_info.assert_called_once()
        mock_client.get_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_update_subsequent(self, hass, device_status, device_info, mock_client):
        """Test subsequent updates don't re-fetch device info."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client
        coordinator.device_info = device_info  # Already fetched

        # Second update should not fetch device info again
        data = await coordinator._async_update_data()

        assert data == device_status
        mock_client.get_device_info.assert_not_called()
        mock_client.get_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_update_failure(self, hass, mock_client):
        """Test update failure handling."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client

        # Make get_status raise an error
        mock_client.get_status.side_effect = NetCommanderError("Connection failed")

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_coordinator_turn_on(self, hass, mock_client):
        """Test turning on an outlet."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client
        coordinator.async_request_refresh = AsyncMock()

        result = await coordinator.async_turn_on(1)

        assert result is True
        mock_client.turn_on.assert_called_once_with(1)
        coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_turn_off(self, hass, mock_client):
        """Test turning off an outlet."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client
        coordinator.async_request_refresh = AsyncMock()

        result = await coordinator.async_turn_off(5)

        assert result is True
        mock_client.turn_off.assert_called_once_with(5)
        coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_reboot_outlet(self, hass, mock_client):
        """Test rebooting an outlet."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client
        coordinator.async_request_refresh = AsyncMock()

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await coordinator.async_reboot_outlet(3)

        assert result is True
        mock_client.turn_off.assert_called_once_with(3)
        mock_client.turn_on.assert_called_once_with(3)
        coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_shutdown(self, hass, mock_client):
        """Test coordinator shutdown."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client

        await coordinator.async_shutdown()

        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_turn_on_error(self, hass, mock_client):
        """Test turn on with error."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client
        mock_client.turn_on.side_effect = NetCommanderError("Command failed")

        result = await coordinator.async_turn_on(1)

        assert result is False

    @pytest.mark.asyncio
    async def test_coordinator_turn_off_error(self, hass, mock_client):
        """Test turn off with error."""
        coordinator = NetCommanderCoordinator(
            hass,
            host="192.168.1.100",
            username="admin",
            password="admin",
        )
        coordinator.client = mock_client
        mock_client.turn_off.side_effect = NetCommanderError("Command failed")

        result = await coordinator.async_turn_off(1)

        assert result is False
