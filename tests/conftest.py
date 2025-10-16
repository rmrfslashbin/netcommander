"""Pytest fixtures for NetCommander tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientSession
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from netcommander import NetCommanderClient, DeviceStatus, DeviceInfo


# Device info fixture
@pytest.fixture
def device_info():
    """Return sample device info."""
    return DeviceInfo(
        model="NP0501DU",
        hardware_version="4.3",
        firmware_version="-7.72-8.5",
        bootloader_version="1.6",
        mac_address="0C:73:EB:B0:9E:5C",
        raw_response="$A0,NP0501DU, HW4.3 BL1.6 -7.72-8.5",
    )


# Device status fixture
@pytest.fixture
def device_status():
    """Return sample device status."""
    return DeviceStatus(
        outlets={1: True, 2: False, 3: True, 4: False, 5: True},
        total_current_amps=2.5,
        temperature="25",
        raw_response="$A0,10101,2.50,25",
    )


# Mock client fixture
@pytest.fixture
def mock_client(device_status, device_info):
    """Return a mock NetCommander client."""
    client = AsyncMock(spec=NetCommanderClient)
    client.get_status = AsyncMock(return_value=device_status)
    client.get_device_info = AsyncMock(return_value=device_info)
    client.turn_on = AsyncMock(return_value=True)
    client.turn_off = AsyncMock(return_value=True)
    client.toggle_outlet = AsyncMock(return_value=True)
    client.turn_on_all = AsyncMock(return_value={1: True, 2: True, 3: True, 4: True, 5: True})
    client.turn_off_all = AsyncMock(return_value={1: True, 2: True, 3: True, 4: True, 5: True})
    client.close = AsyncMock()
    client.host = "192.168.1.100"
    client.username = "admin"
    client.password = "admin"
    return client


# Mock aiohttp response
@pytest.fixture
def mock_response():
    """Return a mock aiohttp response."""
    response = MagicMock()
    response.status = 200
    response.text = AsyncMock(return_value="$A0,10101,2.50,25")
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=None)
    return response


# Mock session
@pytest.fixture
def mock_session(mock_response):
    """Return a mock aiohttp session."""
    session = MagicMock()
    session.get = MagicMock(return_value=mock_response)
    session.close = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


# Connection parameters
@pytest.fixture
def connection_params():
    """Return standard connection parameters."""
    return {
        "host": "192.168.1.100",
        "username": "admin",
        "password": "admin",
    }
