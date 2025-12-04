"""Constants for the Synaccess NetCommander integration."""

DOMAIN = "netcommander"

# Configuration
CONF_SCAN_INTERVAL = "scan_interval"
CONF_REBOOT_DELAY = "reboot_delay"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_COMMAND_DELAY = 0.5  # seconds to wait after command before refresh
DEFAULT_REBOOT_DELAY = 5  # seconds to wait between off and on during reboot

# Device info
MANUFACTURER = "Synaccess"
MODEL = "netCommander"

# Attributes
ATTR_OUTLET_NUMBER = "outlet_number"
ATTR_TOTAL_CURRENT = "total_current_amps"
ATTR_TEMPERATURE = "temperature"
