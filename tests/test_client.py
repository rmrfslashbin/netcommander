"""Tests for NetCommander client."""
import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from netcommander import NetCommanderClient
from netcommander.exceptions import (
    AuthenticationError,
    ConnectionError,
    CommandError,
    InvalidOutletError,
    ParseError,
)


class TestNetCommanderClient:
    """Test NetCommanderClient class."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, connection_params):
        """Test client initialization."""
        client = NetCommanderClient(**connection_params)

        assert client.host == "192.168.1.100"
        assert client.username == "admin"
        assert client.password == "admin"
        assert client.port == 80
        assert client.base_url == "http://192.168.1.100:80/cmd.cgi"

        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self, connection_params, mock_session):
        """Test async context manager."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                assert client._session is not None

    @pytest.mark.asyncio
    async def test_get_status_success(self, connection_params, mock_session):
        """Test successful status retrieval."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0,10101,2.50,25"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                status = await client.get_status()

                assert status.outlets[1] is True
                assert status.outlets[2] is False
                assert status.outlets[3] is True
                assert status.outlets[4] is False
                assert status.outlets[5] is True
                assert status.total_current_amps == 2.50
                assert status.temperature == "25"

    @pytest.mark.asyncio
    async def test_get_status_parse_error(self, connection_params, mock_session):
        """Test status parsing with invalid response."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="INVALID"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                with pytest.raises(ParseError):
                    await client.get_status()

    @pytest.mark.asyncio
    async def test_get_device_info_success(self, connection_params, mock_session):
        """Test successful device info retrieval."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0,NP0501DU, HW4.3 BL1.6 -7.72-8.5"
        )
        mock_session.get.return_value.__aenter__.return_value.status = 200

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                info = await client.get_device_info()

                assert info.model == "NP0501DU"
                assert info.hardware_version == "4.3"
                assert info.firmware_version == "-7.72-8.5"
                assert info.bootloader_version == "1.6"

    @pytest.mark.asyncio
    async def test_turn_on_outlet(self, connection_params, mock_session):
        """Test turning on an outlet."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                result = await client.turn_on(1)
                assert result is True

    @pytest.mark.asyncio
    async def test_turn_off_outlet(self, connection_params, mock_session):
        """Test turning off an outlet."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                result = await client.turn_off(5)
                assert result is True

    @pytest.mark.asyncio
    async def test_toggle_outlet(self, connection_params, mock_session):
        """Test toggling an outlet."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                result = await client.toggle_outlet(3)
                assert result is True

    @pytest.mark.asyncio
    async def test_invalid_outlet_number(self, connection_params):
        """Test invalid outlet number raises error."""
        async with NetCommanderClient(**connection_params) as client:
            with pytest.raises(InvalidOutletError):
                await client.turn_on(0)

            with pytest.raises(InvalidOutletError):
                await client.turn_on(6)

    @pytest.mark.asyncio
    async def test_authentication_error(self, connection_params, mock_session):
        """Test authentication failure."""
        mock_session.get.return_value.__aenter__.return_value.status = 401

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                with pytest.raises(AuthenticationError):
                    await client.get_status()

    @pytest.mark.asyncio
    async def test_command_failure(self, connection_params, mock_session):
        """Test command failure response."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$AF,Error"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                with pytest.raises(CommandError):
                    await client._send_command("$A5")

    @pytest.mark.asyncio
    async def test_turn_on_all(self, connection_params, mock_session):
        """Test turning on all outlets."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                results = await client.turn_on_all()

                assert len(results) == 5
                assert all(results.values())

    @pytest.mark.asyncio
    async def test_turn_off_all(self, connection_params, mock_session):
        """Test turning off all outlets."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                results = await client.turn_off_all()

                assert len(results) == 5
                assert all(results.values())

    @pytest.mark.asyncio
    async def test_get_outlet_state(self, connection_params, mock_session):
        """Test getting individual outlet state."""
        mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="$A0,10101,2.50,25"
        )

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with NetCommanderClient(**connection_params) as client:
                state = await client.get_outlet_state(1)
                assert state is True

                state = await client.get_outlet_state(2)
                assert state is False


class TestStatusParsing:
    """Test status response parsing."""

    def test_parse_all_on(self, connection_params):
        """Test parsing with all outlets on."""
        client = NetCommanderClient(**connection_params)
        response = "$A0,11111,5.00,30"

        status = client._parse_status_response(response)

        assert all(status.outlets.values())
        assert status.total_current_amps == 5.0
        assert status.temperature == "30"

    def test_parse_all_off(self, connection_params):
        """Test parsing with all outlets off."""
        client = NetCommanderClient(**connection_params)
        response = "$A0,00000,0.00,XX"

        status = client._parse_status_response(response)

        assert not any(status.outlets.values())
        assert status.total_current_amps == 0.0
        assert status.temperature == "XX"

    def test_parse_mixed_state(self, connection_params):
        """Test parsing with mixed outlet states."""
        client = NetCommanderClient(**connection_params)
        response = "$A0,01010,1.25,28"

        status = client._parse_status_response(response)

        assert status.outlets[1] is False
        assert status.outlets[2] is True
        assert status.outlets[3] is False
        assert status.outlets[4] is True
        assert status.outlets[5] is False

    def test_parse_invalid_format(self, connection_params):
        """Test parsing invalid response format."""
        client = NetCommanderClient(**connection_params)

        with pytest.raises(ParseError):
            client._parse_status_response("INVALID")

        with pytest.raises(ParseError):
            client._parse_status_response("$A0,123")  # Too few parts


class TestDeviceInfoParsing:
    """Test device info response parsing."""

    def test_parse_complete_info(self, connection_params):
        """Test parsing complete device info."""
        client = NetCommanderClient(**connection_params)
        response = "$A0,NP0501DU, HW4.3 BL1.6 -7.72-8.5"

        info = client._parse_device_info_response(response)

        assert info.model == "NP0501DU"
        assert info.hardware_version == "4.3"
        assert info.firmware_version == "-7.72-8.5"
        assert info.bootloader_version == "1.6"

    def test_parse_minimal_info(self, connection_params):
        """Test parsing minimal device info (model only)."""
        client = NetCommanderClient(**connection_params)
        response = "$A0,NP0501DU"

        info = client._parse_device_info_response(response)

        assert info.model == "NP0501DU"
        assert info.hardware_version is None
        assert info.firmware_version is None
        assert info.bootloader_version is None

    def test_parse_invalid_info(self, connection_params):
        """Test parsing invalid device info."""
        client = NetCommanderClient(**connection_params)

        with pytest.raises(ParseError):
            client._parse_device_info_response("INVALID")

        with pytest.raises(ParseError):
            client._parse_device_info_response("$AF,Error")
