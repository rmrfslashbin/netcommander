"""Async HTTP client for Synaccess netCommander API."""

import logging
import re
from typing import Optional
import aiohttp

from .models import DeviceStatus, OutletState, DeviceInfo
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    CommandError,
    InvalidOutletError,
    ParseError,
)
from .const import (
    CMD_ENDPOINT,
    CMD_GET_STATUS,
    CMD_GET_INFO,
    CMD_SET_OUTLET,
    CMD_TOGGLE_OUTLET,
    RESPONSE_SUCCESS,
    RESPONSE_FAILED,
    NUM_OUTLETS,
    OUTLET_RANGE,
    get_status_position,
    get_rly_index,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class NetCommanderClient:
    """Async client for Synaccess netCommander API.

    This client provides async methods to control and monitor
    Synaccess netCommander/netBooter Power Distribution Units (PDUs).

    Example:
        >>> async with NetCommanderClient("192.168.1.100", "admin", "password") as client:
        ...     status = await client.get_status()
        ...     print(f"Outlet 1 is {'ON' if status.outlets[1] else 'OFF'}")
        ...     await client.set_outlet(1, True)  # Turn ON
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 80,
        timeout: int = DEFAULT_TIMEOUT,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """Initialize the client.

        Args:
            host: Device IP address or hostname
            username: Authentication username
            password: Authentication password
            port: HTTP port (default: 80)
            timeout: Request timeout in seconds (default: 10)
            session: Optional existing aiohttp session (for connection pooling)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}{CMD_ENDPOINT}"

        self._external_session = session is not None
        self._session = session
        self._auth = aiohttp.BasicAuth(username, password)

        _LOGGER.debug(
            "Initialized NetCommanderClient for %s:%d", self.host, self.port
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self) -> None:
        """Ensure we have an active session."""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                auth=self._auth,
                timeout=timeout,
                headers={"User-Agent": "NetCommander-Python/2025.10.15"},
            )
            _LOGGER.debug("Created new aiohttp session")

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._session and not self._external_session:
            await self._session.close()
            self._session = None
            _LOGGER.debug("Closed aiohttp session")

    async def _send_command(self, command: str) -> str:
        """Send a command to the device and return response.

        Args:
            command: Command string (e.g., "$A5", "$A3 1 1", "rly=0")

        Returns:
            Response text from device

        Raises:
            ConnectionError: Cannot reach device
            AuthenticationError: Invalid credentials
            CommandError: Command failed
        """
        await self._ensure_session()

        url = f"{self.base_url}?{command}"
        _LOGGER.debug("Sending command: %s", command)

        try:
            async with self._session.get(url) as resp:
                if resp.status == 401:
                    raise AuthenticationError(
                        f"Authentication failed for {self.username}@{self.host}"
                    )

                if resp.status != 200:
                    raise ConnectionError(
                        self.host, f"HTTP {resp.status}: {resp.reason}"
                    )

                text = await resp.text()
                response = text.strip()
                _LOGGER.debug("Response: %s", response)

                # Check for command failure
                if response.startswith(RESPONSE_FAILED):
                    raise CommandError(command, response)

                return response

        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(self.host, f"Connection failed: {e}")
        except aiohttp.ClientError as e:
            raise ConnectionError(self.host, f"Request error: {e}")

    def _parse_status_response(self, response: str) -> DeviceStatus:
        """Parse status response into DeviceStatus model.

        Format: $A0,XXXXX,C.CC,TT
        - $A0: Success code
        - XXXXX: 5-char outlet string (1=ON, 0=OFF)
        - C.CC: Current in Amps
        - TT: Temperature (or 'XX')

        Args:
            response: Raw response from $A5 command

        Returns:
            DeviceStatus object

        Raises:
            ParseError: Cannot parse response
        """
        try:
            parts = response.split(",")

            if len(parts) < 3:
                raise ParseError(
                    response, f"Expected at least 3 parts, got {len(parts)}"
                )

            if not parts[0].startswith(RESPONSE_SUCCESS):
                raise ParseError(response, f"Expected {RESPONSE_SUCCESS}, got {parts[0]}")

            outlets_str = parts[1]
            if len(outlets_str) != NUM_OUTLETS:
                raise ParseError(
                    response,
                    f"Expected {NUM_OUTLETS} outlet bits, got {len(outlets_str)}",
                )

            # Parse outlets (remember: position 4=outlet1, position 0=outlet5)
            outlets = {}
            for outlet_num in OUTLET_RANGE:
                pos = get_status_position(outlet_num)
                outlets[outlet_num] = outlets_str[pos] == "1"

            # Parse current
            try:
                current = float(parts[2])
            except ValueError:
                raise ParseError(response, f"Invalid current value: {parts[2]}")

            # Parse temperature (may be 'XX')
            temperature = parts[3] if len(parts) > 3 else None

            return DeviceStatus(
                outlets=outlets,
                total_current_amps=current,
                temperature=temperature,
                raw_response=response,
            )

        except IndexError as e:
            raise ParseError(response, f"Index error: {e}")

    async def get_status(self) -> DeviceStatus:
        """Get current status of all outlets and device metrics.

        Returns:
            DeviceStatus with outlet states, current, and temperature

        Raises:
            ConnectionError: Cannot reach device
            AuthenticationError: Invalid credentials
            ParseError: Cannot parse response
        """
        _LOGGER.info("Getting device status")
        response = await self._send_command(CMD_GET_STATUS)
        return self._parse_status_response(response)

    def _parse_device_info_response(self, response: str) -> DeviceInfo:
        """Parse device info response into DeviceInfo model.

        Format: $A0,MODEL, HWX.X BLX.X firmware
        Example: $A0,NP0501DU, HW4.3 BL1.6 -7.72-8.5

        Args:
            response: Raw response from $A8 command

        Returns:
            DeviceInfo object

        Raises:
            ParseError: Cannot parse response
        """
        try:
            if not response.startswith(RESPONSE_SUCCESS + ","):
                raise ParseError(
                    response, f"Expected {RESPONSE_SUCCESS}, got {response[:10]}"
                )

            # Remove "$A0," prefix
            data = response[4:]
            parts = data.split(",")

            if len(parts) < 1:
                raise ParseError(response, "No model information found")

            model = parts[0].strip()
            hardware_version = None
            firmware_version = None
            bootloader_version = None

            if len(parts) >= 2:
                details = parts[1].strip()

                # Parse hardware version
                hw_match = re.search(r"HW\s*([0-9.]+)", details)
                if hw_match:
                    hardware_version = hw_match.group(1)

                # Parse bootloader version
                bl_match = re.search(r"BL\s*([0-9.]+)", details)
                if bl_match:
                    bootloader_version = bl_match.group(1)

                # Parse firmware version (everything after BL)
                fw_match = re.search(r"BL[0-9.]+\s+(.+)", details)
                if fw_match:
                    firmware_version = fw_match.group(1).strip()

            return DeviceInfo(
                model=model,
                hardware_version=hardware_version,
                firmware_version=firmware_version,
                bootloader_version=bootloader_version,
                mac_address=None,  # Will be populated separately if available
                raw_response=response,
            )

        except IndexError as e:
            raise ParseError(response, f"Index error: {e}")

    async def get_device_info(self) -> DeviceInfo:
        """Get device hardware and firmware information.

        Returns:
            DeviceInfo with model, versions, and MAC address

        Raises:
            ConnectionError: Cannot reach device
            AuthenticationError: Invalid credentials
            ParseError: Cannot parse response
        """
        _LOGGER.info("Getting device information")
        response = await self._send_command(CMD_GET_INFO)
        device_info = self._parse_device_info_response(response)

        # Try to get MAC address from web interface
        try:
            await self._ensure_session()
            url = f"http://{self.host}:{self.port}/"
            async with self._session.get(url) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    # Look for MAC address pattern
                    mac_match = re.search(
                        r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", html
                    )
                    if mac_match:
                        # Update device_info with MAC (create new immutable object)
                        device_info = DeviceInfo(
                            model=device_info.model,
                            hardware_version=device_info.hardware_version,
                            firmware_version=device_info.firmware_version,
                            bootloader_version=device_info.bootloader_version,
                            mac_address=mac_match.group(0),
                            raw_response=device_info.raw_response,
                        )
        except Exception as e:
            _LOGGER.debug("Could not get MAC address from web interface: %s", e)

        return device_info

    async def get_outlet_state(self, outlet_number: int) -> bool:
        """Get state of a specific outlet.

        Args:
            outlet_number: Outlet number (1-5)

        Returns:
            True if outlet is ON, False if OFF

        Raises:
            InvalidOutletError: Outlet number out of range
            ConnectionError: Cannot reach device
        """
        if outlet_number not in OUTLET_RANGE:
            raise InvalidOutletError(outlet_number, NUM_OUTLETS)

        _LOGGER.debug("Getting state for outlet %d", outlet_number)
        status = await self.get_status()
        return status.outlets[outlet_number]

    async def set_outlet(self, outlet_number: int, state: bool) -> bool:
        """Set outlet to explicit ON or OFF state.

        IMPORTANT: Uses $A3 command with SPACE syntax (not commas!)

        Args:
            outlet_number: Outlet number (1-5)
            state: True for ON, False for OFF

        Returns:
            True if command succeeded

        Raises:
            InvalidOutletError: Outlet number out of range
            CommandError: Command failed
            ConnectionError: Cannot reach device
        """
        if outlet_number not in OUTLET_RANGE:
            raise InvalidOutletError(outlet_number, NUM_OUTLETS)

        value = 1 if state else 0
        # CRITICAL: Use SPACE between arguments, not comma!
        command = f"{CMD_SET_OUTLET} {outlet_number} {value}"

        _LOGGER.info(
            "Setting outlet %d to %s", outlet_number, "ON" if state else "OFF"
        )

        response = await self._send_command(command)
        return response.startswith(RESPONSE_SUCCESS)

    async def turn_on(self, outlet_number: int) -> bool:
        """Turn outlet ON.

        Args:
            outlet_number: Outlet number (1-5)

        Returns:
            True if command succeeded
        """
        return await self.set_outlet(outlet_number, True)

    async def turn_off(self, outlet_number: int) -> bool:
        """Turn outlet OFF.

        Args:
            outlet_number: Outlet number (1-5)

        Returns:
            True if command succeeded
        """
        return await self.set_outlet(outlet_number, False)

    async def toggle_outlet(self, outlet_number: int) -> bool:
        """Toggle outlet state (ON→OFF or OFF→ON).

        Uses rly command. Note: Less reliable than explicit set_outlet().

        Args:
            outlet_number: Outlet number (1-5)

        Returns:
            True if command succeeded

        Raises:
            InvalidOutletError: Outlet number out of range
        """
        if outlet_number not in OUTLET_RANGE:
            raise InvalidOutletError(outlet_number, NUM_OUTLETS)

        rly_index = get_rly_index(outlet_number)
        command = f"{CMD_TOGGLE_OUTLET}={rly_index}"

        _LOGGER.info("Toggling outlet %d (rly=%d)", outlet_number, rly_index)

        response = await self._send_command(command)
        return response.startswith(RESPONSE_SUCCESS)

    async def turn_on_all(self) -> dict[int, bool]:
        """Turn all outlets ON.

        Returns:
            Dict of outlet_number → success (bool)
        """
        _LOGGER.info("Turning all outlets ON")
        results = {}
        for outlet in OUTLET_RANGE:
            try:
                results[outlet] = await self.turn_on(outlet)
            except Exception as e:
                _LOGGER.error("Failed to turn on outlet %d: %s", outlet, e)
                results[outlet] = False
        return results

    async def turn_off_all(self) -> dict[int, bool]:
        """Turn all outlets OFF.

        Returns:
            Dict of outlet_number → success (bool)
        """
        _LOGGER.info("Turning all outlets OFF")
        results = {}
        for outlet in OUTLET_RANGE:
            try:
                results[outlet] = await self.turn_off(outlet)
            except Exception as e:
                _LOGGER.error("Failed to turn off outlet %d: %s", outlet, e)
                results[outlet] = False
        return results
