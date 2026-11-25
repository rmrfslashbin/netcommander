"""
Synaccess netCommander API Client Library.

A Python library for controlling Synaccess netCommander/netBooter PDUs.
"""

from .client import NetCommanderClient
from .exceptions import (
    AuthenticationError,
    CommandError,
    NetCommanderConnectionError,
    NetCommanderError,
)
from .models import DeviceInfo, DeviceStatus, OutletConfig, OutletState

__version__ = "2025.12.4.2"
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
    "NetCommanderConnectionError",
    "CommandError",
]
