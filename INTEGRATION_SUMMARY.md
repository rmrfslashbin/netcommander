# Home Assistant Integration Summary

## Overview

The NetCommander Home Assistant integration is complete and ready for testing. This integration provides full control and monitoring of Synaccess netCommander PDUs through Home Assistant.

## What Was Built

### 1. Core Integration Files

#### `__init__.py`
- Entry point for the integration
- Sets up the coordinator
- Manages platform loading (switch, sensor, button)
- Handles integration lifecycle (setup, unload, reload)

#### `manifest.json`
- Integration metadata
- Dependencies: `aiohttp>=3.9.0`, `pydantic>=1.10.0`
- Version: 2025.10.15
- Integration type: `device`
- IoT class: `local_polling`

#### `const.py`
- Domain and configuration constants
- Default scan interval: 30 seconds
- Device manufacturer and model info
- Attribute names for entities

### 2. Configuration Flow

#### `config_flow.py`
- UI-based setup through Settings → Devices & Services
- Validates connection and credentials
- Fetches device info for unique ID (uses MAC address)
- Error handling for connection and authentication issues
- Prevents duplicate configurations

#### `strings.json` + `translations/en.json`
- User-facing text for config flow
- Error messages
- Form labels and descriptions

### 3. Data Coordinator

#### `coordinator.py`
- Manages data updates from the device
- Polls device every 30 seconds (configurable)
- Fetches device info on first update
- Provides methods for entity actions:
  - `async_turn_on(outlet_number)` - Turn outlet on
  - `async_turn_off(outlet_number)` - Turn outlet off
  - `async_reboot_outlet(outlet_number)` - Power cycle outlet
- Handles errors and raises `UpdateFailed` on communication issues
- Manages client session lifecycle

### 4. Entity Platforms

#### `switch.py` - Outlet Control
- **5 Switch Entities** (one per outlet)
- Entity IDs: `switch.netcommander_outlet_1` through `switch.netcommander_outlet_5`
- Features:
  - Turn on/off individual outlets
  - Reports current state from coordinator data
  - Includes outlet number in attributes
  - Linked to device with full device info

#### `sensor.py` - Monitoring
- **3 Sensor Entities** for device metrics

**Total Current Sensor:**
- Entity ID: `sensor.netcommander_total_current`
- Unit: Amperes (A)
- Device class: `current`
- State class: `measurement`
- Tracks total power draw across all outlets

**Temperature Sensor:**
- Entity ID: `sensor.netcommander_temperature`
- Unit: Celsius (°C)
- Device class: `temperature`
- State class: `measurement`
- Shows device temperature (if available)

**Outlets On Sensor:**
- Entity ID: `sensor.netcommander_outlets_on`
- Icon: `mdi:power-socket`
- State class: `measurement`
- Count of currently powered outlets

#### `button.py` - Reboot Functionality
- **5 Button Entities** (one per outlet)
- Entity IDs: `button.netcommander_reboot_outlet_1` through `button.netcommander_reboot_outlet_5`
- Icon: `mdi:restart`
- Action: Power cycle (turn off → wait 5 seconds → turn on)
- Useful for remotely rebooting connected equipment

### 5. Device Information

Each entity reports comprehensive device information:
- **Name**: Synaccess {model}
- **Manufacturer**: Synaccess
- **Model**: NP0501DU (from device)
- **Software Version**: Firmware version (e.g., -7.72-8.5)
- **Hardware Version**: Hardware version (e.g., 4.3)
- **Connections**: MAC address

All entities are grouped under a single device in Home Assistant.

### 6. HACS Support

#### `hacs.json`
- HACS metadata file
- Enables installation through HACS
- Requires Home Assistant 2024.1.0+

## Entity Summary

| Entity Type | Count | Purpose |
|-------------|-------|---------|
| Switch | 5 | Control individual outlets ON/OFF |
| Sensor | 3 | Monitor current, temperature, outlet count |
| Button | 5 | Reboot/power cycle outlets |
| **Total** | **13** | **Complete device control and monitoring** |

## Integration Features

### ✅ UI Configuration
- No YAML required
- Guided setup with validation
- Clear error messages

### ✅ Device Management
- Single device entry in Home Assistant
- All entities grouped under device
- Full device metadata display

### ✅ Real-time Updates
- Automatic polling (30 seconds default)
- Optimistic updates on state changes
- Coordinated data fetching

### ✅ Error Handling
- Connection error recovery
- Authentication validation
- Graceful degradation

### ✅ Standards Compliant
- Follows Home Assistant entity guidelines
- Uses standard device classes
- Proper state classes for statistics

### ✅ HACS Compatible
- Custom repository support
- One-click installation
- Automatic updates

## Testing Checklist

### Initial Setup
- [ ] Install integration via HACS or manual copy
- [ ] Restart Home Assistant
- [ ] Add integration through UI
- [ ] Enter device IP, username, password
- [ ] Verify successful connection

### Entity Verification
- [ ] Check 5 switch entities appear
- [ ] Check 3 sensor entities appear
- [ ] Check 5 button entities appear
- [ ] Verify all entities show in device page

### Functionality Tests
- [ ] Toggle individual outlets via switches
- [ ] Verify state changes in UI
- [ ] Check current sensor updates
- [ ] Check temperature sensor (if supported)
- [ ] Test reboot button functionality
- [ ] Verify outlets_on count is accurate

### Edge Cases
- [ ] Test with device offline (should show unavailable)
- [ ] Test with wrong credentials (should show error)
- [ ] Test reload integration
- [ ] Test remove and re-add integration

### Home Assistant Features
- [ ] Create automations with switches
- [ ] Use sensors in dashboards
- [ ] Set up alerts on current draw
- [ ] Create scripts with reboot buttons

## Next Steps

1. **Basic Testing**
   - Install in development Home Assistant instance
   - Verify all entities work correctly
   - Test state updates and controls

2. **Documentation**
   - Screenshots for README
   - Example automations
   - Lovelace card examples

3. **HACS Submission**
   - Create GitHub release
   - Submit to HACS default repository
   - Add to Home Assistant integrations list

4. **Community Feedback**
   - Request testing on other device models
   - Gather feature requests
   - Address any compatibility issues

## Files Created

```
custom_components/netcommander/
├── __init__.py              # Integration setup and lifecycle
├── manifest.json            # Integration metadata
├── hacs.json               # HACS metadata
├── const.py                # Constants and configuration
├── config_flow.py          # UI configuration flow
├── coordinator.py          # Data update coordinator
├── switch.py               # Switch platform (5 entities)
├── sensor.py               # Sensor platform (3 entities)
├── button.py               # Button platform (5 entities)
├── strings.json            # English strings (config flow)
└── translations/
    └── en.json             # English translations
```

## Integration Architecture

```
User adds integration via UI
         ↓
config_flow.py validates connection
         ↓
__init__.py creates NetCommanderCoordinator
         ↓
coordinator.py connects to device via NetCommanderClient
         ↓
Platforms create entities (switch, sensor, button)
         ↓
Coordinator polls device every 30 seconds
         ↓
Entities update state from coordinator data
```

## Key Implementation Details

### Coordinator Pattern
- Single coordinator instance per integration
- All entities subscribe to coordinator
- Coordinator manages client session
- Efficient data fetching (one request updates all entities)

### Device Linkage
- All entities linked to single device via entry_id
- Device info populated from `get_device_info()` API call
- MAC address used for unique device identification

### State Management
- Entities are `CoordinatorEntity` subclasses
- Automatic state updates on coordinator refresh
- Manual refresh triggered after state changes

### Async First
- All I/O operations are async
- Non-blocking integration with Home Assistant
- Efficient use of resources

## Notes

- Integration uses the shared `netcommander` library from `src/`
- Path injection used in coordinator and config_flow to import library
- Pydantic v1 compatibility (Home Assistant requirement)
- Default credentials: admin/admin (should be changed!)
- Device must be on local network (no cloud support)
