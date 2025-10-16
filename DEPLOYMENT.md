# Home Assistant Integration - Deployment Guide

## Current Status: ✅ READY FOR USE

The NetCommander Home Assistant integration is complete and ready for deployment!

## What's Included

### Integration Files
```
custom_components/netcommander/
├── __init__.py              # Integration setup
├── manifest.json            # Integration metadata
├── config_flow.py          # UI configuration
├── coordinator.py          # Data coordinator
├── const.py                # Constants
├── switch.py               # 5 switch entities (outlets)
├── sensor.py               # 3 sensor entities (current, temp, count)
├── button.py               # 5 button entities (reboot)
├── hacs.json               # HACS metadata
├── strings.json            # UI strings
├── translations/
│   └── en.json            # English translations
└── lib/
    └── netcommander/      # Bundled API client library
        ├── __init__.py
        ├── client.py
        ├── models.py
        ├── exceptions.py
        └── const.py
```

### Entities Created (13 total)
- **5 Switches**: Control individual outlets (ON/OFF)
- **3 Sensors**: Total current (A), temperature (°C), outlets on count
- **5 Buttons**: Reboot/power cycle individual outlets

## Installation Methods

### Method 1: HACS (Recommended for Users)

**Prerequisites:**
- [HACS](https://hacs.xyz/) installed in Home Assistant
- Home Assistant 2024.1.0 or higher

**Steps:**
1. In Home Assistant, go to **HACS → Integrations**
2. Click **⋮** (three dots) → **Custom repositories**
3. Add repository URL: `https://github.com/rmrfslashbin/netcommander`
4. Category: **Integration**
5. Click **Add**
6. Search for "NetCommander" and click **Download**
7. Restart Home Assistant
8. Go to **Settings → Devices & Services → Add Integration**
9. Search for "Synaccess NetCommander"
10. Enter your device details:
    - **IP Address**: `192.168.x.x`
    - **Username**: `admin` (default)
    - **Password**: Your device password

### Method 2: Manual Installation

**For Home Assistant:**
```bash
# SSH into Home Assistant or use terminal addon
cd /config

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Copy the integration
# Option A: Clone entire repo then copy
git clone https://github.com/rmrfslashbin/netcommander.git /tmp/netcommander
cp -r /tmp/netcommander/custom_components/netcommander custom_components/

# Option B: Download release and extract
wget https://github.com/rmrfslashbin/netcommander/releases/latest/download/netcommander.zip
unzip netcommander.zip -d custom_components/

# Restart Home Assistant
# Settings → System → Restart
```

**For Home Assistant OS/Container:**
1. Use File Editor addon or Samba share
2. Copy `custom_components/netcommander/` to `/config/custom_components/`
3. Restart Home Assistant

### Method 3: Development/Testing

**For local development:**
```bash
# From this repository
cd /path/to/homeassistant/config
ln -s /path/to/netcommander/custom_components/netcommander custom_components/netcommander

# Restart Home Assistant
```

## Configuration

### Adding the Integration

1. **Settings → Devices & Services → Add Integration**
2. Search for "**Synaccess NetCommander**"
3. Enter connection details:
   - **IP Address or Hostname**: `192.168.1.100`
   - **Username**: `admin` (default)
   - **Password**: Your device password (default: `admin`)
4. Click **Submit**

The integration will:
- Connect to your device
- Fetch device information (model, firmware, MAC)
- Create all entities automatically
- Start polling every 30 seconds

### Entity IDs

After setup, you'll have:

**Switches:**
- `switch.netcommander_np0501du_outlet_1`
- `switch.netcommander_np0501du_outlet_2`
- `switch.netcommander_np0501du_outlet_3`
- `switch.netcommander_np0501du_outlet_4`
- `switch.netcommander_np0501du_outlet_5`

**Sensors:**
- `sensor.netcommander_np0501du_total_current`
- `sensor.netcommander_np0501du_temperature`
- `sensor.netcommander_np0501du_outlets_on`

**Buttons:**
- `button.netcommander_np0501du_reboot_outlet_1`
- ... through outlet 5

## Usage Examples

### Automation: Turn on outlet when sun sets

```yaml
automation:
  - alias: "Turn on outdoor lights at sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.netcommander_np0501du_outlet_1
```

### Automation: Alert on high current draw

```yaml
automation:
  - alias: "Alert on high power usage"
    trigger:
      - platform: numeric_state
        entity_id: sensor.netcommander_np0501du_total_current
        above: 10
    action:
      - service: notify.mobile_app
        data:
          message: "PDU current draw is {{ states('sensor.netcommander_np0501du_total_current') }}A"
```

### Script: Reboot device on schedule

```yaml
script:
  reboot_server:
    alias: "Reboot Server"
    sequence:
      - service: button.press
        target:
          entity_id: button.netcommander_np0501du_reboot_outlet_3
```

### Dashboard Card

```yaml
type: entities
title: PDU Control
entities:
  - entity: sensor.netcommander_np0501du_total_current
  - entity: sensor.netcommander_np0501du_temperature
  - entity: sensor.netcommander_np0501du_outlets_on
  - type: divider
  - entity: switch.netcommander_np0501du_outlet_1
  - entity: switch.netcommander_np0501du_outlet_2
  - entity: switch.netcommander_np0501du_outlet_3
  - entity: switch.netcommander_np0501du_outlet_4
  - entity: switch.netcommander_np0501du_outlet_5
```

## Troubleshooting

### Integration not showing up

1. Verify files are in correct location:
   ```bash
   ls /config/custom_components/netcommander/
   ```
2. Check logs: **Settings → System → Logs**
3. Look for errors containing "netcommander"
4. Restart Home Assistant

### Cannot connect to device

1. Verify device IP address is correct
2. Ping device: `ping 192.168.x.x`
3. Check device web interface is accessible
4. Verify credentials (default: admin/admin)
5. Check Home Assistant can reach device network

### Entities not updating

1. Check device is online
2. Look for errors in logs
3. Try reloading integration:
   - **Settings → Devices & Services**
   - Find NetCommander
   - Click **⋮** → **Reload**

### Factory Reset Device (if needed)

If device shows incorrect states or won't respond:
1. Hold reset button for **20 seconds**
2. Wait for device to reboot
3. Reconfigure network settings
4. Remove and re-add integration in Home Assistant

## Updating

### Via HACS
1. **HACS → Integrations**
2. Find "Synaccess NetCommander"
3. Click **Update** if available
4. Restart Home Assistant

### Manual Update
1. Download latest release
2. Replace `custom_components/netcommander/` directory
3. Restart Home Assistant

## Uninstalling

1. **Settings → Devices & Services**
2. Find "Synaccess NetCommander"
3. Click **⋮** → **Delete**
4. Confirm deletion
5. (Optional) Remove files:
   ```bash
   rm -rf /config/custom_components/netcommander
   ```
6. Restart Home Assistant

## Device Compatibility

**Tested:**
- ✅ Synaccess netBooter NP-0501DU (5 outlets)
  - Firmware: -7.72-8.5
  - Hardware: 4.3

**Likely Compatible:**
- Other Synaccess netCommander models
- netBooter series PDUs

**Please report compatibility!** Open an issue at:
https://github.com/rmrfslashbin/netcommander/issues

## Support

### Getting Help

1. **Check Logs**: Settings → System → Logs
2. **Documentation**: See README.md and INSTALLATION.md
3. **GitHub Issues**: https://github.com/rmrfslashbin/netcommander/issues
4. **Home Assistant Community**: Tag @rmrfslashbin

### Reporting Issues

Include:
- Home Assistant version
- Integration version
- Device model and firmware
- Error messages from logs
- Steps to reproduce

## Security Notes

1. **Change default password!** Default is `admin/admin`
2. Use strong password for device
3. Keep device on isolated/trusted network
4. Regularly update firmware
5. Monitor access logs

## Performance

- **Polling Interval**: 30 seconds (configurable in code)
- **Resource Usage**: Minimal (async HTTP requests)
- **Network Impact**: ~1 request every 30 seconds
- **Latency**: Commands execute in <1 second

## Advanced Configuration

### Changing Poll Interval

Edit `custom_components/netcommander/const.py`:
```python
DEFAULT_SCAN_INTERVAL = 30  # Change to desired seconds
```

### Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.netcommander: debug
```

## What's Next?

- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Request features
- 🤝 Contribute improvements
- 📝 Share your automations

## License

MIT License - See LICENSE file

## Author

Robert Sigler (code@sigler.io)

---

**Made with ❤️ for the Home Assistant community**
