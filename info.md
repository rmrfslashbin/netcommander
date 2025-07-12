## Synaccess netCommander Integration

A Home Assistant custom component for controlling Synaccess netCommander Power Distribution Units (PDUs).

### Features

- 🔌 **Outlet Control**: Turn individual outlets ON/OFF
- 📊 **Real-time Monitoring**: Current draw per outlet and total consumption  
- 🌡️ **Temperature Monitoring**: Device temperature sensors
- 🔄 **Auto-Discovery**: Automatically detects all available outlets
- 🛡️ **Robust Authentication**: Secure HTTP Basic Authentication

### Installation Requirements

1. **Network access** to your netCommander device
2. **Device credentials** (username and password)
3. **Home Assistant 2023.1.0** or newer

### Quick Setup

1. Add your device IP address and credentials
2. Ensure web control is unlocked in device settings
3. Integration will auto-discover all outlets and sensors

### Important Notes

- **Unlock web control**: In your device's web interface, go to **Outlet Setup** and ensure **"Lock Web Outlet ON/OFF And Reboot Operation"** is **unchecked**
- **Default credentials**: Many devices use `admin/admin`
- **Supported models**: Tested with NP-0501DU, other models should work

For detailed setup instructions and troubleshooting, see the [full documentation](https://github.com/rmrfslashbin/netcommander#readme).