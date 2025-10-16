"""Data models for netCommander API client."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OutletState(BaseModel):
    """State of a single outlet."""

    outlet_number: int = Field(ge=1, le=5, description="Outlet number (1-5)")
    is_on: bool = Field(description="Outlet power state (True=ON, False=OFF)")

    class Config:
        frozen = True  # Immutable


class OutletConfig(BaseModel):
    """Configuration for an outlet."""

    outlet_number: int = Field(ge=1, le=5)
    name: Optional[str] = Field(default=None, description="Friendly name")
    description: Optional[str] = Field(default=None, description="Description")

    @validator("outlet_number")
    def validate_outlet_number(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError(f"Outlet number must be 1-5, got {v}")
        return v


class DeviceInfo(BaseModel):
    """Device hardware and firmware information."""

    model: str = Field(description="Device model number (e.g., NP0501DU)")
    hardware_version: Optional[str] = Field(
        default=None, description="Hardware version"
    )
    firmware_version: Optional[str] = Field(
        default=None, description="Firmware version"
    )
    bootloader_version: Optional[str] = Field(
        default=None, description="Bootloader version"
    )
    mac_address: Optional[str] = Field(
        default=None, description="MAC address"
    )
    raw_response: str = Field(description="Raw device response from $A8")

    class Config:
        frozen = True  # Immutable


class DeviceStatus(BaseModel):
    """Complete device status including all outlets and metrics."""

    outlets: dict[int, bool] = Field(
        description="Outlet states keyed by outlet number (1-5)"
    )
    total_current_amps: float = Field(
        ge=0.0, description="Total current draw in Amps"
    )
    temperature: Optional[str] = Field(
        default=None, description="Temperature reading (may be 'XX' if unavailable)"
    )
    raw_response: str = Field(description="Raw device response")

    @validator("outlets")
    def validate_outlets(cls, v: dict[int, bool]) -> dict[int, bool]:
        """Ensure all 5 outlets are present."""
        expected_outlets = set(range(1, 6))
        actual_outlets = set(v.keys())

        if actual_outlets != expected_outlets:
            raise ValueError(
                f"Expected outlets {expected_outlets}, got {actual_outlets}"
            )

        return v

    def get_outlet_state(self, outlet_number: int) -> bool:
        """Get state of specific outlet."""
        if outlet_number not in self.outlets:
            raise ValueError(f"Invalid outlet number: {outlet_number}")
        return self.outlets[outlet_number]

    @property
    def all_on(self) -> bool:
        """Check if all outlets are ON."""
        return all(self.outlets.values())

    @property
    def all_off(self) -> bool:
        """Check if all outlets are OFF."""
        return not any(self.outlets.values())

    @property
    def outlets_on(self) -> list[int]:
        """Get list of outlet numbers that are ON."""
        return [num for num, state in self.outlets.items() if state]

    @property
    def outlets_off(self) -> list[int]:
        """Get list of outlet numbers that are OFF."""
        return [num for num, state in self.outlets.items() if not state]

    class Config:
        frozen = True  # Immutable
