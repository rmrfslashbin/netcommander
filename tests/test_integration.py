"""Integration tests for NetCommander.

These tests require a real device to be available.
Set environment variables to enable:
  NETCOMMANDER_HOST=192.168.1.100
  NETCOMMANDER_PASSWORD=admin
  RUN_INTEGRATION_TESTS=1
"""
import pytest
import os
import sys
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from netcommander import NetCommanderClient


# Skip integration tests unless explicitly enabled
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Integration tests require RUN_INTEGRATION_TESTS=1"
)


@pytest.fixture
def integration_config():
    """Get configuration for integration tests."""
    host = os.getenv("NETCOMMANDER_HOST")
    password = os.getenv("NETCOMMANDER_PASSWORD", "admin")
    username = os.getenv("NETCOMMANDER_USER", "admin")

    if not host:
        pytest.skip("NETCOMMANDER_HOST not set")

    return {
        "host": host,
        "username": username,
        "password": password,
    }


class TestIntegration:
    """Integration tests with real device."""

    @pytest.mark.asyncio
    async def test_get_device_info(self, integration_config):
        """Test getting device info from real device."""
        async with NetCommanderClient(**integration_config) as client:
            info = await client.get_device_info()

            assert info.model is not None
            assert len(info.model) > 0
            print(f"\nDevice: {info.model}")
            print(f"Hardware: {info.hardware_version}")
            print(f"Firmware: {info.firmware_version}")
            print(f"MAC: {info.mac_address}")

    @pytest.mark.asyncio
    async def test_get_status(self, integration_config):
        """Test getting status from real device."""
        async with NetCommanderClient(**integration_config) as client:
            status = await client.get_status()

            assert status.outlets is not None
            assert len(status.outlets) == 5
            assert status.total_current_amps >= 0
            print(f"\nOutlets: {status.outlets}")
            print(f"Current: {status.total_current_amps}A")
            print(f"Temperature: {status.temperature}")

    @pytest.mark.asyncio
    async def test_outlet_control(self, integration_config):
        """Test controlling an outlet (outlet 1)."""
        async with NetCommanderClient(**integration_config) as client:
            # Get initial state
            initial_status = await client.get_status()
            initial_state = initial_status.outlets[1]
            print(f"\nOutlet 1 initial state: {'ON' if initial_state else 'OFF'}")

            # Turn off
            await client.turn_off(1)
            await asyncio.sleep(2)
            status = await client.get_status()
            assert status.outlets[1] is False
            print("Outlet 1 turned OFF")

            # Turn on
            await client.turn_on(1)
            await asyncio.sleep(2)
            status = await client.get_status()
            assert status.outlets[1] is True
            print("Outlet 1 turned ON")

            # Restore initial state
            if initial_state:
                await client.turn_on(1)
            else:
                await client.turn_off(1)
            print(f"Outlet 1 restored to: {'ON' if initial_state else 'OFF'}")

    @pytest.mark.asyncio
    async def test_toggle_outlet(self, integration_config):
        """Test toggling an outlet (outlet 2)."""
        async with NetCommanderClient(**integration_config) as client:
            # Get initial state
            initial_status = await client.get_status()
            initial_state = initial_status.outlets[2]
            print(f"\nOutlet 2 initial state: {'ON' if initial_state else 'OFF'}")

            # Toggle
            await client.toggle_outlet(2)
            await asyncio.sleep(2)
            status = await client.get_status()
            assert status.outlets[2] == (not initial_state)
            print(f"Outlet 2 toggled to: {'ON' if status.outlets[2] else 'OFF'}")

            # Toggle back
            await client.toggle_outlet(2)
            await asyncio.sleep(2)
            status = await client.get_status()
            assert status.outlets[2] == initial_state
            print(f"Outlet 2 toggled back to: {'ON' if initial_state else 'OFF'}")

    @pytest.mark.asyncio
    async def test_get_outlet_state(self, integration_config):
        """Test getting individual outlet state."""
        async with NetCommanderClient(**integration_config) as client:
            for outlet_num in range(1, 6):
                state = await client.get_outlet_state(outlet_num)
                print(f"Outlet {outlet_num}: {'ON' if state else 'OFF'}")
                assert isinstance(state, bool)

    @pytest.mark.asyncio
    async def test_current_monitoring(self, integration_config):
        """Test current monitoring during state changes."""
        async with NetCommanderClient(**integration_config) as client:
            # Get initial current
            initial_status = await client.get_status()
            initial_current = initial_status.total_current_amps
            print(f"\nInitial current: {initial_current}A")

            # Turn on outlet 3
            await client.turn_on(3)
            await asyncio.sleep(2)

            on_status = await client.get_status()
            on_current = on_status.total_current_amps
            print(f"Current with outlet 3 ON: {on_current}A")

            # Turn off outlet 3
            await client.turn_off(3)
            await asyncio.sleep(2)

            off_status = await client.get_status()
            off_current = off_status.total_current_amps
            print(f"Current with outlet 3 OFF: {off_current}A")

            # Current should change (unless outlet had no load)
            assert on_status.outlets[3] is True
            assert off_status.outlets[3] is False


class TestIntegrationErrorHandling:
    """Test error handling with real device."""

    @pytest.mark.asyncio
    async def test_invalid_outlet(self, integration_config):
        """Test invalid outlet numbers."""
        from netcommander.exceptions import InvalidOutletError

        async with NetCommanderClient(**integration_config) as client:
            with pytest.raises(InvalidOutletError):
                await client.turn_on(0)

            with pytest.raises(InvalidOutletError):
                await client.turn_on(6)

    @pytest.mark.asyncio
    async def test_session_reuse(self, integration_config):
        """Test reusing client session."""
        async with NetCommanderClient(**integration_config) as client:
            # Make multiple calls with same session
            info = await client.get_device_info()
            status1 = await client.get_status()
            status2 = await client.get_status()

            assert info.model is not None
            assert status1.outlets is not None
            assert status2.outlets is not None
