"""Tests for NetCommander data models."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from netcommander.models import DeviceStatus, DeviceInfo, OutletState


class TestDeviceStatus:
    """Test DeviceStatus model."""

    def test_create_device_status(self):
        """Test creating a DeviceStatus object."""
        status = DeviceStatus(
            outlets={1: True, 2: False, 3: True, 4: False, 5: True},
            total_current_amps=2.5,
            temperature="25",
            raw_response="$A0,10101,2.50,25",
        )

        assert status.outlets[1] is True
        assert status.outlets[2] is False
        assert status.total_current_amps == 2.5
        assert status.temperature == "25"

    def test_outlets_on_property(self):
        """Test outlets_on property."""
        status = DeviceStatus(
            outlets={1: True, 2: False, 3: True, 4: False, 5: False},
            total_current_amps=1.0,
            temperature="20",
            raw_response="$A0,01000,1.00,20",
        )

        outlets_on = status.outlets_on
        assert len(outlets_on) == 2
        assert 1 in outlets_on
        assert 3 in outlets_on

    def test_outlets_off_property(self):
        """Test outlets_off property."""
        status = DeviceStatus(
            outlets={1: True, 2: False, 3: True, 4: False, 5: False},
            total_current_amps=1.0,
            temperature="20",
            raw_response="$A0,01000,1.00,20",
        )

        outlets_off = status.outlets_off
        assert len(outlets_off) == 3
        assert 2 in outlets_off
        assert 4 in outlets_off
        assert 5 in outlets_off

    def test_all_on(self):
        """Test status with all outlets on."""
        status = DeviceStatus(
            outlets={1: True, 2: True, 3: True, 4: True, 5: True},
            total_current_amps=5.0,
            temperature="30",
            raw_response="$A0,11111,5.00,30",
        )

        assert len(status.outlets_on) == 5
        assert len(status.outlets_off) == 0

    def test_all_off(self):
        """Test status with all outlets off."""
        status = DeviceStatus(
            outlets={1: False, 2: False, 3: False, 4: False, 5: False},
            total_current_amps=0.0,
            temperature="XX",
            raw_response="$A0,00000,0.00,XX",
        )

        assert len(status.outlets_on) == 0
        assert len(status.outlets_off) == 5


class TestDeviceInfo:
    """Test DeviceInfo model."""

    def test_create_device_info_complete(self):
        """Test creating a complete DeviceInfo object."""
        info = DeviceInfo(
            model="NP0501DU",
            hardware_version="4.3",
            firmware_version="-7.72-8.5",
            bootloader_version="1.6",
            mac_address="0C:73:EB:B0:9E:5C",
            raw_response="$A0,NP0501DU, HW4.3 BL1.6 -7.72-8.5",
        )

        assert info.model == "NP0501DU"
        assert info.hardware_version == "4.3"
        assert info.firmware_version == "-7.72-8.5"
        assert info.bootloader_version == "1.6"
        assert info.mac_address == "0C:73:EB:B0:9E:5C"

    def test_create_device_info_minimal(self):
        """Test creating DeviceInfo with minimal fields."""
        info = DeviceInfo(
            model="NP0501DU",
            raw_response="$A0,NP0501DU",
        )

        assert info.model == "NP0501DU"
        assert info.hardware_version is None
        assert info.firmware_version is None
        assert info.bootloader_version is None
        assert info.mac_address is None

    def test_device_info_optional_fields(self):
        """Test DeviceInfo with some optional fields."""
        info = DeviceInfo(
            model="NP0501DU",
            hardware_version="4.3",
            raw_response="$A0,NP0501DU, HW4.3",
        )

        assert info.model == "NP0501DU"
        assert info.hardware_version == "4.3"
        assert info.firmware_version is None
        assert info.bootloader_version is None


class TestOutletState:
    """Test OutletState model."""

    def test_outlet_state_on(self):
        """Test OutletState with ON state."""
        state = OutletState(outlet_number=1, is_on=True)
        assert state.outlet_number == 1
        assert state.is_on is True

    def test_outlet_state_off(self):
        """Test OutletState with OFF state."""
        state = OutletState(outlet_number=5, is_on=False)
        assert state.outlet_number == 5
        assert state.is_on is False

    def test_outlet_state_invalid_number(self):
        """Test OutletState with invalid outlet number."""
        with pytest.raises(Exception):  # Pydantic validation error
            OutletState(outlet_number=0, is_on=True)

        with pytest.raises(Exception):
            OutletState(outlet_number=6, is_on=False)
