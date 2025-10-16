# Installation Guide

## Home Assistant Integration

### Option 1: HACS Installation (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. In Home Assistant, go to HACS → Integrations
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/rmrfslashbin/netcommander` as an Integration
6. Click "Install"
7. Restart Home Assistant
8. Go to Settings → Devices & Services
9. Click "Add Integration"
10. Search for "Synaccess NetCommander"
11. Follow the configuration steps

### Option 2: Manual Installation

1. Copy the `custom_components/netcommander` folder to your Home Assistant `custom_components` directory:
   ```bash
   cd /path/to/homeassistant/config
   mkdir -p custom_components
   cp -r /path/to/netcommander/custom_components/netcommander custom_components/
   ```

2. Copy the shared library:
   ```bash
   cp -r /path/to/netcommander/src/netcommander custom_components/netcommander/
   ```

3. Restart Home Assistant

4. Go to Settings → Devices & Services → Add Integration → "Synaccess NetCommander"

### Configuration

When adding the integration, you'll need:
- **IP Address**: The local IP address of your NetCommander device (e.g., `192.168.1.100`)
- **Username**: Default is `admin`
- **Password**: Default is `admin` (change this on your device!)

## CLI Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/rmrfslashbin/netcommander.git
cd netcommander

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[cli]"
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/rmrfslashbin/netcommander.git
cd netcommander

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with CLI dependencies
pip install -e ".[cli]"
```

### Environment Setup

Create a `.env` file in the project root:

```bash
NETCOMMANDER_HOST=192.168.1.100
NETCOMMANDER_USER=admin
NETCOMMANDER_PASSWORD=admin
```

Or use command-line options:

```bash
python -m netcommander_cli.cli --host 192.168.1.100 --password admin status
```

## Requirements

- Python 3.11 or higher
- Home Assistant 2024.1.0 or higher (for HA integration)
- Network access to the NetCommander device

## Tested Devices

- Synaccess netBooter NP-0501DU (5 outlets)
- Firmware: -7.72-8.5
- Hardware: 4.3

Other Synaccess netCommander/netBooter models may work but are untested. Please report your results!

## Troubleshooting

### Connection Issues

1. Verify the device IP address is correct:
   ```bash
   ping 192.168.1.100
   ```

2. Test with the CLI first:
   ```bash
   python -m netcommander_cli.cli --host 192.168.1.100 --password admin info
   ```

3. Check that your device uses HTTP (not HTTPS) on port 80

### Authentication Issues

1. Verify credentials by accessing the web interface: `http://192.168.1.100`
2. Default credentials are username: `admin`, password: `admin`
3. If you changed the password, update your configuration

### Device Not Responding

1. Factory reset: Hold the reset button for 20 seconds
2. Check network connectivity
3. Verify no firewall is blocking port 80
