# NP-0501DU Definitive Outlet Mapping

**Device**: Synaccess netBooter NP-0501DU
**Test Date**: 2025-10-15
**Status**: ✅ COMPLETE - All 5 outlets tested
**Critical Finding**: 🚨 **ALL OUTLETS HAVE INVERTED LOGIC**

---

## Executive Summary

**CRITICAL HARDWARE ISSUE**: The NP-0501DU reports the **inverse** of the actual outlet state for **ALL outlets**.

- When an outlet has **POWER** → Device reports `0` (OFF)
- When an outlet has **NO POWER** → Device reports `1` (ON)
- LED indicators match device status (not physical power)
- This affects **ALL 5 outlets consistently**

---

## Complete Mapping Table

| Physical Outlet | Control Command | Status Position | LED Behavior | Logic Type |
|----------------|-----------------|-----------------|--------------|------------|
| 1 | `rly=0` | Position 4 (rightmost) | Matches device status | **INVERTED** |
| 2 | `rly=1` | Position 3 | Matches device status | **INVERTED** |
| 3 | `rly=2` | Position 2 | Matches device status | **INVERTED** |
| 4 | `rly=3` | Position 1 | Matches device status | **INVERTED** |
| 5 | `rly=4` | Position 0 (leftmost) | Matches device status | **INVERTED** |

---

## Detailed Findings

### Control Mapping
The control mapping is **linear and predictable**:
```
rly=0 → Physical Outlet 1
rly=1 → Physical Outlet 2
rly=2 → Physical Outlet 3
rly=3 → Physical Outlet 4
rly=4 → Physical Outlet 5

Formula: Physical Outlet = rly_index + 1
```

### Status String Mapping
Status format: `$A0,XXXXX,current,temp`

The 5-character outlet string maps as documented:
```
Position:  [0]    [1]    [2]    [3]    [4]
Outlet:     5      4      3      2      1
rly:        4      3      2      1      0
```

**Formula**: `status_position = 4 - outlet_number`

---

## Inverted Logic Analysis

### Pattern Observed (ALL OUTLETS - Consistent)

#### Initial State (outlets have power, LEDs off)
```
LED:          OFF
Power:        ON  ← Physical reality
Device Says:  0   ← Reports OFF (WRONG!)
Status:       00000
Current:      0.10A (confirms power draw)
```

#### After Toggle (LED on, no power)
```
LED:          ON  ← Matches device status
Power:        OFF ← Physical reality
Device Says:  1   ← Reports ON (WRONG!)
Status:       XXXXX (bit flipped to 1)
Current:      0.09A (drops - confirms power cut)
```

#### After Second Toggle (back to initial)
```
LED:          OFF
Power:        ON  ← Physical reality restored
Device Says:  0   ← Reports OFF (WRONG!)
Status:       00000
Current:      0.10A (back to baseline)
```

---

## LED Indicator Behavior

**Finding**: LEDs are wired to follow **device status**, not actual power state.

- LED ON = Device thinks outlet is ON (but outlet is actually OFF)
- LED OFF = Device thinks outlet is OFF (but outlet is actually ON)
- **LED is NOT a reliable indicator of power state**

This is a **safety hazard** - you cannot trust the visual indicators!

---

## Evidence Summary

### Outlet 1
- Initial: LED=OFF, Power=ON, Status=0 (inverted ✗)
- Toggle:  LED=ON,  Power=OFF, Status=1 (inverted ✗)
- Restore: LED=OFF, Power=ON, Status=0 (inverted ✗)

### Outlet 2
- Initial: LED=OFF, Power=ON, Status=0 (inverted ✗)
- Toggle:  LED=ON,  Power=OFF, Status=1 (inverted ✗)
- Restore: LED=OFF, Power=ON, Status=0 (inverted ✗)

### Outlet 3
- Initial: LED=OFF, Power=ON, Status=0 (inverted ✗)
- Toggle:  LED=ON,  Power=OFF, Status=1 (inverted ✗)
- Restore: LED=OFF, Power=ON, Status=0 (inverted ✗)

### Outlet 4
- Initial: LED=OFF, Power=ON, Status=0 (inverted ✗)
- Toggle:  LED=ON,  Power=OFF, Status=1 (inverted ✗)
- Restore: LED=OFF, Power=ON, Status=0 (inverted ✗)

### Outlet 5
- Initial: LED=OFF, Power=ON, Status=0 (inverted ✗)
- Toggle:  LED=ON,  Power=OFF, Status=1 (inverted ✗)
- Restore: LED=OFF, Power=ON, Status=0 (inverted ✗)

**100% consistent across all outlets** - This is systematic, not random.

---

## Current Draw Analysis

Confirms physical power state:
- When outlets have power: **0.10A** (base load)
- When outlets are off: **0.09A** (slightly lower - confirms cut)
- Delta: **0.01A** per outlet toggle

This validates that power is actually being cut despite status showing "ON".

---

## Root Cause Hypothesis

This appears to be either:

1. **Firmware bug** - Status bits inverted in software
2. **Hardware design** - Relay wiring uses "Normally Closed" logic
3. **Configuration issue** - Device has a setting that's wrong

**Recommendation**: Contact Synaccess support with this data.

---

## Software Implementation Requirements

### For All Software (HA, CLI, API)

**MUST implement logic inversion for NP-0501DU**:

```python
def get_actual_power_state(device_status_bit: str) -> bool:
    """Convert device status to actual power state.

    NP-0501DU reports inverted status:
    - Device says '0' (OFF) → Outlet has POWER
    - Device says '1' (ON)  → Outlet is OFF
    """
    return device_status_bit == "0"  # Inverted!

def get_desired_status_bit(want_power_on: bool) -> str:
    """Convert desired power state to device status bit.

    To turn outlet ON (give it power), device status must show '0'
    To turn outlet OFF (cut power), device status must show '1'
    """
    return "0" if want_power_on else "1"  # Inverted!
```

### Configuration

Must support per-device configuration:
```python
DEVICE_CONFIGS = {
    "NP-0501DU": {
        "inverted_logic": True,
        "all_outlets": True,  # Affects all outlets
    },
    # Other models might not have this issue
}
```

---

## API Mapping Reference

### Get Status
```python
# Example: $A0,00000,0.10,XX with all outlets powered ON

outlets_string = "00000"

# Parse each position
for i, bit in enumerate(outlets_string):
    outlet_num = 5 - i  # Position 0=Outlet5, Position 4=Outlet1
    device_says = bit   # '0' or '1'

    # Apply inversion for NP-0501DU
    has_power = (device_says == "0")  # INVERTED!

    print(f"Outlet {outlet_num}: {has_power}")

# Output:
# Outlet 5: True  (bit='0')
# Outlet 4: True  (bit='0')
# Outlet 3: True  (bit='0')
# Outlet 2: True  (bit='0')
# Outlet 1: True  (bit='0')
```

### Set Outlet State
```python
def set_outlet(outlet_num: int, want_power: bool):
    # Get current status
    status = get_status()  # Returns "00000"

    # Find status position for this outlet
    status_pos = 4 - (outlet_num - 1)  # Outlet 1 → pos 4

    # Determine desired status bit (INVERTED!)
    desired_bit = "0" if want_power else "1"

    # Check current bit
    current_bit = status[status_pos]

    # If already in desired state, do nothing
    if current_bit == desired_bit:
        return  # Already correct

    # Need to toggle
    rly_index = outlet_num - 1
    send_command(f"rly={rly_index}")
```

---

## Safety Warnings

### ⚠️ CRITICAL SAFETY ISSUES

1. **Visual indicators are wrong** - LED ON = outlet OFF
2. **Web UI is wrong** - Shows opposite of reality
3. **Status API is wrong** - Reports inverse of power state
4. **Trust nothing but physical testing** - Use meter/load to verify

### Potential Hazards

- Attempting maintenance on "powered off" equipment that's actually ON
- Unexpected power cycles due to inverted control logic
- Equipment damage from incorrect state assumptions
- Data loss from unintended power interruptions

### Mitigation

- **Always verify with physical testing** (multimeter, load testing)
- **Software MUST implement inversion logic**
- **Document clearly in user-facing interfaces** that status is corrected
- **Add warning in HA** that LEDs don't match actual state

---

## Next Steps

1. ✅ **DONE**: Complete mapping verified
2. ⏳ **TODO**: Contact Synaccess support about firmware issue
3. ⏳ **TODO**: Check if web interface has configuration option
4. ⏳ **TODO**: Test firmware update (if available)
5. ⏳ **TODO**: Implement inversion in all software components
6. ⏳ **TODO**: Add device detection/auto-configure in client library
7. ⏳ **TODO**: Document for other NP-0501DU users

---

**Last Updated**: 2025-10-15
**Test Data**: `outlet_mapping_results_20251015_131625.json`
**Status**: Complete and verified
