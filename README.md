# Synaccess NetCommander

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/rmrfslashbin/netcommander.svg)](https://github.com/rmrfslashbin/netcommander/releases)
[![License](https://img.shields.io/github/license/rmrfslashbin/netcommander.svg)](LICENSE)

Complete control solution for Synaccess netCommander/netBooter Power Distribution Units (PDUs). Includes both a Home Assistant custom component and a standalone CLI tool, built on a shared async Python API client library.

## Features

### Home Assistant Integration
- **Switch Entities**: Control each outlet individually (ON/OFF)
- **Sensor Entities**: Monitor total current, temperature, and active outlet count
- **Button Entities**: Reboot outlets (power cycle: off → wait → on)
- **Device Info**: View model, firmware version, hardware version, and MAC address
- **Real-time Updates**: Configurable polling interval (default: 30 seconds)
- **UI Configuration**: Easy setup through Home Assistant's UI

### CLI Tool
- **Interactive Commands**: Control outlets, monitor status, view device info
- **Multiple Output Formats**: Table (Rich), JSON, YAML
- **Real-time Monitoring**: Live dashboard with auto-refresh
- **Batch Operations**: Turn all outlets on/off at once
- **Environment Config**: Support for `.env` files and command-line arguments

### API Client Library
- **Async First**: Built with `aiohttp` for high performance
- **Type Safe**: Pydantic models for data validation
- **Exception Handling**: Custom exception hierarchy
- **Session Management**: Connection pooling and automatic cleanup

## Supported Devices

**Tested:**
- Synaccess netBooter NP-0501DU (5 outlets)
  - Firmware: -7.72-8.5
  - Hardware: 4.3

**Potentially Compatible:**
- Other Synaccess netCommander models
- netBooter series PDUs

*Please report your device compatibility results via GitHub issues!*

## Quick Start

### Home Assistant (HACS)

1. Add this repository to HACS as a custom repository
2. Install "Synaccess NetCommander"
3. Restart Home Assistant
4. Add integration: Settings → Devices & Services → Add Integration → "Synaccess NetCommander"
5. Enter device IP, username (default: `admin`), and password

### CLI

```bash
# Install with uv
git clone https://github.com/rmrfslashbin/netcommander.git
cd netcommander
uv venv && source .venv/bin/activate
uv pip install -e ".[cli]"

# Create .env file
cat > .env << EOF
NETCOMMANDER_HOST=192.168.1.100
NETCOMMANDER_USER=admin
NETCOMMANDER_PASSWORD=admin
EOF

# Run commands
python -m netcommander_cli.cli status
python -m netcommander_cli.cli outlet 1 on
python -m netcommander_cli.cli monitor
python -m netcommander_cli.cli info
```

## CLI Usage

```bash
# Show status (table format)
netcommander status

# Show status as JSON
netcommander status --output json

# Control outlets
netcommander outlet 1 on
netcommander outlet 5 off
netcommander outlet 3 toggle

# Control all outlets
netcommander all on
netcommander all off

# Real-time monitoring
netcommander monitor --interval 2

# Device information
netcommander info
```

## Home Assistant Entities

After adding the integration, you'll get:

### Switches (5)
- `switch.netcommander_outlet_1` through `switch.netcommander_outlet_5`
- Control individual outlets

### Sensors (3)
- `sensor.netcommander_total_current` - Total current draw in Amps
- `sensor.netcommander_temperature` - Device temperature in °C
- `sensor.netcommander_outlets_on` - Count of powered outlets

### Buttons (5)
- `button.netcommander_reboot_outlet_1` through `button.netcommander_reboot_outlet_5`
- Power cycle outlets (useful for rebooting connected devices)

## API Usage

```python
import asyncio
from netcommander import NetCommanderClient

async def main():
    async with NetCommanderClient("192.168.1.100", "admin", "admin") as client:
        # Get device info
        info = await client.get_device_info()
        print(f"Model: {info.model}, Firmware: {info.firmware_version}")

        # Get status
        status = await client.get_status()
        print(f"Outlet 1: {'ON' if status.outlets[1] else 'OFF'}")
        print(f"Current: {status.total_current_amps}A")

        # Control outlets
        await client.turn_on(1)
        await client.turn_off(5)
        await client.toggle_outlet(3)

        # Batch operations
        await client.turn_on_all()

asyncio.run(main())
```

## Architecture

```
┌─────────────────────────────────────┐
│   Home Assistant Integration        │
│   - Config Flow                     │
│   - Coordinator                     │
│   - Switch/Sensor/Button Entities   │
└──────────────┬──────────────────────┘
               │
               │ imports
               ▼
┌─────────────────────────────────────┐
│   Shared API Client Library         │
│   - NetCommanderClient              │
│   - Async HTTP with aiohttp         │
│   - Pydantic Models                 │
│   - Custom Exceptions               │
└──────────────┬──────────────────────┘
               │
               │ imports
               ▲
┌──────────────┴──────────────────────┐
│   CLI Tool                           │
│   - Click commands                   │
│   - Rich tables & formatting        │
│   - Real-time monitor               │
└─────────────────────────────────────┘
```

## Device API Commands

The integration uses these HTTP commands:
- `$A5` - Get status (outlets, current, temperature)
- `$A8` - Get device info (model, versions)
- `$A3 {port} {value}` - Set outlet state (SPACES not commas!)
- `rly={index}` - Toggle outlet

## Troubleshooting

### Factory Reset
If your device shows inverted logic or commands fail:
1. Hold reset button for 20 seconds
2. Release when status light changes
3. Reconfigure network settings

### Connection Issues
```bash
# Test with CLI first
python -m netcommander_cli.cli --host 192.168.1.100 --password admin info

# Check network
ping 192.168.1.100

# Verify web interface accessible
curl http://192.168.1.100
```

See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting.

## Development

```bash
# Clone and setup
git clone https://github.com/rmrfslashbin/netcommander.git
cd netcommander
uv venv && source .venv/bin/activate

# Install all dependencies
uv pip install -e ".[cli,ha,dev]"

# Run tests
make test

# Lint
make lint
```

## Project Structure

```
netcommander/
├── src/netcommander/          # Shared API client library
│   ├── client.py              # Main async client
│   ├── models.py              # Pydantic data models
│   ├── exceptions.py          # Custom exceptions
│   └── const.py               # Constants
├── netcommander_cli/          # CLI tool
│   └── cli.py                 # Click commands
├── custom_components/         # Home Assistant integration
│   └── netcommander/
│       ├── __init__.py        # Integration setup
│       ├── manifest.json      # Integration metadata
│       ├── config_flow.py     # UI configuration
│       ├── coordinator.py     # Data coordinator
│       ├── switch.py          # Switch entities
│       ├── sensor.py          # Sensor entities
│       └── button.py          # Button entities
└── tests/                     # Test scripts
```

## Contributing

Contributions welcome! Please:
1. Test with your device and report compatibility
2. Submit issues for bugs or feature requests
3. Create pull requests with improvements

## Author

Robert Sigler (code@sigler.io)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the Home Assistant community**
