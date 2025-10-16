"""Constants for netCommander API client."""

# Default connection settings
DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_PORT = 80

# Command endpoints
CMD_ENDPOINT = "/cmd.cgi"

# Commands
CMD_GET_STATUS = "$A5"
CMD_GET_INFO = "$A8"  # Get device information
CMD_SET_OUTLET = "$A3"  # Format: "$A3 {port} {value}" (SPACES!)
CMD_TOGGLE_OUTLET = "rly"  # Format: "rly={index}"

# Response codes
RESPONSE_SUCCESS = "$A0"
RESPONSE_FAILED = "$AF"

# Outlet configuration for NP-0501DU
NUM_OUTLETS = 5
OUTLET_RANGE = range(1, NUM_OUTLETS + 1)

# Status string position mapping
# Position 0 (leftmost) = Outlet 5
# Position 4 (rightmost) = Outlet 1
def get_status_position(outlet_number: int) -> int:
    """Get status string position for outlet number (1-5)."""
    return NUM_OUTLETS - outlet_number

def get_rly_index(outlet_number: int) -> int:
    """Get rly index for outlet number (1-5)."""
    return outlet_number - 1

# Default credentials (should be changed!)
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
