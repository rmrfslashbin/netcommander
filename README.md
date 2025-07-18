# Synaccess netCommander Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/rmrfslashbin/netcommander.svg)](https://github.com/rmrfslashbin/netcommander/releases)
[![License](https://img.shields.io/github/license/rmrfslashbin/netcommander.svg)](LICENSE)

A Home Assistant custom component for controlling Synaccess netCommander Power Distribution Units (PDUs). This integration provides real-time monitoring and control of outlet states, current draw, and device temperature.

## Features

- 🔌 **Outlet Control**: Turn individual outlets ON/OFF
- 📊 **Real-time Monitoring**: Current draw per outlet and total consumption
- 🌡️ **Temperature Monitoring**: Device temperature sensors
- 🔄 **Auto-Discovery**: Automatically detects all available outlets
- 🛡️ **Robust Authentication**: Secure HTTP Basic Authentication
- 📱 **Native HA Integration**: Switches, sensors, and device management

## Supported Devices

### Tested Device
This integration has been **verified and tested** with:
- **Synaccess netBooter™ Model: NP-0501DU** (5-outlet model)

### Compatibility with Other Models
The integration is designed to work with **most Synaccess netCommander/netBooter devices** that feature:
- Web interface with HTTP Basic Authentication
- Command-line interface accessible via `/cmd.cgi` endpoint
- Status command (`$A5`) and control commands (`rly=X`, `rb=X`)

**Potentially compatible models include:**
- Other netBooter™ series (NP-0501, NP-0201, etc.)
- netCommander series devices
- Models with similar web interface architecture

### ⚠️ Important Notes
- **Physical outlet mapping may vary** between models - you may need to test which HA entity controls which physical outlet
- **Some models may require different authentication** or command formats
- **Outlet counts will vary** - the integration dynamically detects available outlets

### 🤝 Community Testing
**Help us expand compatibility!** If you successfully use this integration with other Synaccess models:

1. **Test thoroughly** - verify outlet control, monitoring, and reboot functions
2. **Note any mapping differences** - which HA entities control which physical outlets  
3. **Submit a pull request** or **open an issue** with:
   - Device model number
   - Firmware version
   - Any configuration changes needed
   - Outlet mapping details

**Your contribution helps the community!** 🎉

## Installation via HACS

### Prerequisites

1. **HACS** must be installed in your Home Assistant instance
2. **Network access** to your netCommander device
3. **Device credentials** (username and password)

### Step 1: Add Custom Repository

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click the **three dots menu** (⋮) in the top right
4. Select **Custom repositories**
5. Add this repository:
   ```
   Repository: rmrfslashbin/netcommander
   Category: Integration
   ```
6. Click **Add**

### Step 2: Install Integration

1. Search for **"Synaccess netCommander"** in HACS
2. Click **Download**
3. Select the latest version
4. **Restart Home Assistant**

### Step 3: Configure Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"Synaccess netCommander"**
4. Enter your device details:
   - **Host**: IP address of your netCommander (e.g., `192.168.1.100`)
   - **Username**: Device username (default: `admin`)
   - **Password**: Device password
5. Click **Submit**

## Manual Installation

If you prefer manual installation:

1. Download the latest release from [GitHub Releases](https://github.com/rmrfslashbin/netcommander/releases)
2. Extract the `custom_components/netcommander` folder
3. Copy it to your Home Assistant `custom_components` directory:
   ```
   config/
   └── custom_components/
       └── netcommander/
           ├── __init__.py
           ├── api.py
           ├── config_flow.py
           ├── const.py
           ├── coordinator.py
           ├── manifest.json
           ├── sensor.py
           └── switch.py
   ```
4. Restart Home Assistant
5. Follow **Step 3** from the HACS installation

## Configuration

### Device Setup

1. **Enable Web Interface**: Ensure your netCommander's web interface is accessible
2. **Check Credentials**: Verify you can log into the device at `http://[device-ip]/`
3. **Unlock Control** (if needed): In the device web interface, go to **Outlet Setup** and ensure **"Lock Web Outlet ON/OFF And Reboot Operation"** is **unchecked**

### Integration Options

After adding the integration, you can configure:

- **Update Interval**: How often to poll the device (default: 30 seconds)
- **Timeout**: Request timeout for device communication

## Entities Created

The integration creates the following entities:

### Switches
- `switch.netcommander_outlet_1` - Physical Outlet 5 control
- `switch.netcommander_outlet_2` - Physical Outlet 4 control
- `switch.netcommander_outlet_3` - Physical Outlet 3 control
- `switch.netcommander_outlet_4` - Physical Outlet 2 control  
- `switch.netcommander_outlet_5` - Physical Outlet 1 control

### Sensors
- `sensor.netcommander_total_current` - Total current draw (A)
- `sensor.netcommander_temperature` - Device temperature (°C)

**Note**: The integration maps HA entities to physical outlets based on the device's internal numbering. Entity names display the actual physical outlet numbers.

## Troubleshooting

### Common Issues

#### Authentication Failed
- **Check credentials**: Verify username/password work in web browser
- **Check IP address**: Ensure Home Assistant can reach the device
- **Try default credentials**: Many devices use `admin/admin`

#### Control Not Working
- **Unlock web control**: Go to device **Outlet Setup** page
- **Uncheck "Lock Web Outlet ON/OFF And Reboot Operation"**
- **Restart integration** after unlocking

#### Connection Timeout
- **Check network**: Ensure Home Assistant and device are on same network
- **Check firewall**: Ensure port 80 is accessible
- **Try browser test**: Access `http://[device-ip]/cmd.cgi?$A5` manually

### Advanced Debugging

Enable debug logging by adding to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.netcommander: debug
```

Then check **Settings** → **System** → **Logs** for detailed information.

## API Reference

The integration uses the device's web interface with these endpoints:

- **Status**: `GET /cmd.cgi?$A5` - Get outlet states and sensor data
- **Control**: `GET /cmd.cgi?rly=X` - Toggle outlet X (0-4, reverse mapped)
- **Authentication**: HTTP Basic Auth with device credentials

**Device Mapping**: The device uses reverse numbering where `rly=0` controls the last physical outlet.

## Development

### Setting Up Development Environment

1. **Clone repository**:
   ```bash
   git clone https://github.com/rmrfslashbin/netcommander.git
   cd netcommander
   ```

2. **Set up environment**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements-dev.txt
   ```

3. **Configure credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your device details
   ```

4. **Run tests**:
   ```bash
   python test_auth.py  # Test authentication
   python netcommander_api.py  # Test full API
   ```

### Project Structure

```
netcommander/
├── custom_components/netcommander/  # Home Assistant integration
├── netcommander_api.py             # Standalone API client
├── test_*.py                       # Test scripts
├── CONTROL-FINDINGS.md             # Technical analysis
├── DEV-SETUP.md                   # Development guide
└── requirements-dev.txt           # Development dependencies
```

## Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration. Synaccess Networks is not affiliated with this project. Use at your own risk.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rmrfslashbin/netcommander/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/rmrfslashbin/netcommander/discussions)
- 📖 **Documentation**: [Technical Findings](CONTROL-FINDINGS.md)

---

**Made with ❤️ for the Home Assistant community**