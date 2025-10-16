"""Custom exceptions for netCommander API client."""


class NetCommanderError(Exception):
    """Base exception for all netCommander errors."""

    pass


class AuthenticationError(NetCommanderError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class ConnectionError(NetCommanderError):
    """Raised when cannot connect to device."""

    def __init__(self, host: str, message: str = "Cannot connect to device"):
        self.host = host
        self.message = f"{message}: {host}"
        super().__init__(self.message)


class CommandError(NetCommanderError):
    """Raised when a command fails."""

    def __init__(self, command: str, response: str = "$AF"):
        self.command = command
        self.response = response
        self.message = f"Command failed: {command} (response: {response})"
        super().__init__(self.message)


class InvalidOutletError(NetCommanderError):
    """Raised when outlet number is out of range."""

    def __init__(self, outlet: int, max_outlets: int = 5):
        self.outlet = outlet
        self.max_outlets = max_outlets
        self.message = f"Invalid outlet number: {outlet} (must be 1-{max_outlets})"
        super().__init__(self.message)


class ParseError(NetCommanderError):
    """Raised when cannot parse device response."""

    def __init__(self, response: str, reason: str = "Invalid format"):
        self.response = response
        self.reason = reason
        self.message = f"Parse error ({reason}): {response}"
        super().__init__(self.message)
