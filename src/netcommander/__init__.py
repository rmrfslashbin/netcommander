"""
Synaccess netCommander API Client Library.

A Python library for controlling Synaccess netCommander/netBooter PDUs.
"""

from .client import NetCommanderClient
from .models import DeviceStatus, OutletState, OutletConfig, DeviceInfo
from .exceptions import (
    NetCommanderError,
    AuthenticationError,
    ConnectionError,
    CommandError,
)

__version__ = "2025.10.15"
__author__ = "Robert Sigler"
__email__ = "code@sigler.io"

__all__ = [
    "NetCommanderClient",
    "DeviceStatus",
    "OutletState",
    "OutletConfig",
    "DeviceInfo",
    "NetCommanderError",
    "AuthenticationError",
    "ConnectionError",
    "CommandError",
]
