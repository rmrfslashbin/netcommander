# NP-0501DU API Specification - VERIFIED

**Device**: Synaccess netBooter NP-0501DU
**Test Date**: 2025-10-15
**Status**: ✅ COMPLETE - Device working correctly after factory reset
**Firmware**: Unknown (check web interface)

---

## Executive Summary

After factory reset, the NP-0501DU works **perfectly**:
- ✅ **No inverted logic** - Status matches reality
- ✅ **LEDs match power state** - Visual indicators are accurate
- ✅ **Explicit ON/OFF control** - Full API support
- ✅ **All commands work** - Status, control, and toggle all functional

**Critical Discovery**: The manual documentation is **incorrect**. HTTP commands use **SPACES**, not commas.

---

## Working HTTP Commands

### Base URL Format
```
http://{device_ip}/cmd.cgi?{command}
```

### Authentication
- **Type**: HTTP Basic Auth
- **Username**: admin (default)
- **Password**: admin (default, should be changed)

---

## Command Reference

### 1. Get Status - `$A5`

**Query status of all outlets**

```bash
GET http://192.168.1.100/cmd.cgi?$A5
```

**Response Format:**
```
$A0,XXXXX,C.CC,TT\r\n\r\n\r\n
```

**Fields:**
- `$A0` - Success code
- `XXXXX` - 5-character outlet state string
  - Each character: `1` = ON, `0` = OFF
  - Position mapping (RIGHT to LEFT):
    - Position 4 (rightmost): Outlet 1
    - Position 3: Outlet 2
    - Position 2: Outlet 3
    - Position 1: Outlet 4
    - Position 0 (leftmost): Outlet 5
- `C.CC` - Total current draw in Amps
- `TT` - Temperature (may show `XX` if not available)

**Examples:**
```
$A0,00000,0.06,XX  → All outlets OFF, 0.06A draw
$A0,00001,0.15,XX  → Outlet 1 ON, others OFF, 0.15A
$A0,11111,0.85,XX  → All outlets ON, 0.85A
$A0,10001,0.25,XX  → Outlets 1 and 5 ON
```

**Parsing Status String:**
```python
def parse_status(status_str: str) -> dict:
    parts = status_str.strip().split(",")
    return {
        "code": parts[0],           # $A0 = success, $AF = fail
        "outlets": parts[1],        # 5-char string
        "current_amps": float(parts[2]),
        "temperature": parts[3],
    }

def get_outlet_state(outlets_str: str, outlet_num: int) -> bool:
    """Get state of specific outlet (1-5)"""
    position = 5 - outlet_num  # Outlet 1 → pos 4, outlet 5 → pos 0
    return outlets_str[position] == '1'
```

---

### 2. Set Outlet (Explicit) - `$A3 port value`

**⚠️ IMPORTANT: Use SPACES, not commas!**

**Turn outlet explicitly ON or OFF**

```bash
# Turn outlet 1 ON
GET http://192.168.1.100/cmd.cgi?$A3 1 1

# Turn outlet 1 OFF
GET http://192.168.1.100/cmd.cgi?$A3 1 0

# Turn outlet 5 ON
GET http://192.168.1.100/cmd.cgi?$A3 5 1
```

**Parameters:**
- `port` - Outlet number (1-5)
- `value` - State (`1` = ON, `0` = OFF)

**Response:**
```
$A0\r\n\r\n        → Success
$AF\r\n\r\n        → Failed
```

**Note**: The manual documents this as `$A3,port,value` (with commas), but the HTTP interface requires **SPACES**.

---

### 3. Toggle Outlet - `rly=X`

**Toggle outlet state (ON→OFF or OFF→ON)**

```bash
# Toggle outlet 1
GET http://192.168.1.100/cmd.cgi?rly=0

# Toggle outlet 5
GET http://192.168.1.100/cmd.cgi?rly=4
```

**Parameters:**
- `X` - Relay index (0-4)
  - `rly=0` → Outlet 1
  - `rly=1` → Outlet 2
  - `rly=2` → Outlet 3
  - `rly=3` → Outlet 4
  - `rly=4` → Outlet 5

**Response:**
```
$A0\r\n\r\n        → Success
```

**Note**: Toggle is useful but requires checking current state first. Use `$A3` for explicit control.

---

## Complete Outlet Mapping

| Physical Outlet | Status Position | Status Bit Mask | Control ($A3) | Toggle (rly) |
|----------------|-----------------|-----------------|---------------|--------------|
| 1 | 4 (rightmost) | `0b00001` | `$A3 1 X` | `rly=0` |
| 2 | 3 | `0b00010` | `$A3 2 X` | `rly=1` |
| 3 | 2 | `0b00100` | `$A3 3 X` | `rly=2` |
| 4 | 1 | `0b01000` | `$A3 4 X` | `rly=3` |
| 5 | 0 (leftmost) | `0b10000` | `$A3 5 X` | `rly=4` |

---

## Commands That DON'T Work via HTTP

These commands are documented in the manual but **return `$AF` (failed)** via HTTP:

- ❌ `$A3,port,value` - Explicit control with **commas** (use spaces instead!)
- ❌ `$A7,value` - Set all outlets ON/OFF
- ❌ `/pset n x` - Serial-style command
- ❌ `$A1,user,pass` - Login (authentication is HTTP Basic only)

**These may work via Telnet (port 23) but are not supported via HTTP.**

---

## Error Codes

| Code | Meaning |
|------|---------|
| `$A0` | Success |
| `$AF` | Failed / Unknown command |

---

## API Client Implementation

### Basic Python Example

```python
import requests
from typing import Optional

class NetCommanderClient:
    def __init__(self, host: str, username: str, password: str):
        self.base_url = f"http://{host}/cmd.cgi"
        self.auth = (username, password)

    def get_status(self) -> dict:
        """Get outlet status and metrics."""
        response = requests.get(f"{self.base_url}?$A5", auth=self.auth)
        parts = response.text.strip().split(",")

        return {
            "outlets": {
                1: parts[1][4] == '1',  # Position 4
                2: parts[1][3] == '1',  # Position 3
                3: parts[1][2] == '1',  # Position 2
                4: parts[1][1] == '1',  # Position 1
                5: parts[1][0] == '1',  # Position 0
            },
            "total_current_amps": float(parts[2]),
            "temperature": parts[3],
        }

    def set_outlet(self, outlet: int, state: bool) -> bool:
        """Set outlet explicitly ON (True) or OFF (False)."""
        value = 1 if state else 0
        # IMPORTANT: Use space between arguments!
        url = f"{self.base_url}?$A3 {outlet} {value}"
        response = requests.get(url, auth=self.auth)
        return response.text.strip().startswith("$A0")

    def toggle_outlet(self, outlet: int) -> bool:
        """Toggle outlet state."""
        rly_index = outlet - 1
        url = f"{self.base_url}?rly={rly_index}"
        response = requests.get(url, auth=self.auth)
        return response.text.strip().startswith("$A0")

# Usage
client = NetCommanderClient("192.168.1.100", "admin", "admin")

# Turn on outlet 1
client.set_outlet(1, True)

# Get status
status = client.get_status()
print(f"Outlet 1 is {'ON' if status['outlets'][1] else 'OFF'}")
print(f"Total current: {status['total_current_amps']}A")

# Turn off all outlets
for outlet in range(1, 6):
    client.set_outlet(outlet, False)
```

---

## Device Behavior

### After Factory Reset
- All outlets: **OFF**
- IP: `192.168.1.100`
- User/Pass: `admin/admin`
- Status: `$A0,00000,0.06,XX` (or similar low current)

### Normal Operation
- **LED indicators match outlet state** ✓
- **Status bits match physical power** ✓
- **No inverted logic** ✓
- **Explicit commands work** ✓

### Current Draw
- Base consumption: ~0.06-0.10A (device itself)
- Per-outlet load: Varies by connected device
- Monitoring current can help detect:
  - Power loss (sudden drop)
  - Short circuits (sudden spike)
  - Equipment failure (unexpected change)

---

## Security Recommendations

1. **Change default password** immediately after setup
2. **Use HTTPS** if device supports it (check model variant)
3. **Isolate on management network** - PDUs shouldn't be on public internet
4. **Use strong passwords** - Default `admin/admin` is insecure
5. **Disable unused protocols** - Check if Telnet/SNMP can be disabled
6. **Monitor access logs** - If available in web interface

---

## Web Interface

- **URL**: `http://{device_ip}/`
- **Default Login**: admin / admin
- **Features**:
  - Outlet control (ON/OFF/Reboot)
  - Network configuration
  - User management
  - Outlet naming/grouping
  - AutoPing configuration
  - Firmware upgrade

**Check web interface for:**
- Current firmware version
- Serial number
- Model information
- Advanced configuration options

---

## Known Issues & Limitations

### Documentation Errors
- ❌ Manual shows `$A3,port,value` (commas) - **WRONG**
- ✅ Actual syntax: `$A3 port value` (spaces) - **CORRECT**

### HTTP Limitations
- Cannot set all outlets at once via `$A7`
- Must use individual `$A3` commands for each outlet
- Login command `$A1` doesn't work (use HTTP Basic Auth)

### Temperature Sensor
- May show `XX` instead of actual temperature
- Check firmware/hardware version
- May require calibration or not be present

---

## Testing & Verification

All tests performed: 2025-10-15
- ✅ Status query ($A5)
- ✅ Explicit ON ($A3 port 1)
- ✅ Explicit OFF ($A3 port 0)
- ✅ Toggle (rly=X)
- ✅ All outlets (1-5)
- ✅ LED verification
- ✅ Power verification
- ✅ Status accuracy

**Test files:**
- `test_device_discovery.py` - Initial discovery
- `test_command_formats.py` - Command syntax testing
- `test_correct_syntax.py` - Explicit control verification

---

## Reference Documents

- Device Manual: `1291_NPCStartup_v13.pdf`
- Test Results: `outlet_mapping_results_*.json`
- Factory Reset Guide: `FACTORY_RESET_GUIDE.md`
- Old (broken) mapping: `OUTLET_MAPPING.md` (pre-reset)

---

**Last Updated**: 2025-10-15
**Status**: Complete and verified
**Device State**: Working correctly after factory reset
